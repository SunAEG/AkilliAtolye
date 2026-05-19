-- =============================================================
-- Migration 002: Trigger, Function ve Procedure tanımları
-- =============================================================

-- ---------------------------------------------------------------
-- FUNCTION: updated_at otomatik güncelleme
-- ---------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_users_updated_at   ON users;
DROP TRIGGER IF EXISTS trg_roles_updated_at   ON roles;
DROP TRIGGER IF EXISTS trg_screens_updated_at ON screens;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_screens_updated_at
    BEFORE UPDATE ON screens
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

-- ---------------------------------------------------------------
-- FUNCTION: Tablo değişikliklerini logs'a yaz
-- ---------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_log_table_changes()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_old_val   JSONB;
    v_new_val   JSONB;
    v_record_id BIGINT;
    v_action    TEXT;
BEGIN
    IF TG_OP = 'DELETE' THEN
        v_old_val   := to_jsonb(OLD);
        v_new_val   := NULL;
        v_record_id := OLD.id;
        v_action    := 'DELETE';
    ELSIF TG_OP = 'UPDATE' THEN
        v_old_val   := to_jsonb(OLD);
        v_new_val   := to_jsonb(NEW);
        v_record_id := NEW.id;
        v_action    := 'UPDATE';
    ELSE
        v_old_val   := NULL;
        v_new_val   := to_jsonb(NEW);
        v_record_id := NEW.id;
        v_action    := 'CREATE';
    END IF;

    INSERT INTO logs (value) VALUES (
        jsonb_build_object(
            'action',              v_action,
            'table_name',         TG_TABLE_NAME,
            'record_id',          v_record_id,
            'old_value',          v_old_val,
            'new_value',          v_new_val,
            'triggered_at',       to_char(NOW(), 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
            'rabbitmq_published', false,
            'status',             'SUCCESS',
            'source',             'db_trigger'
        )
    );

    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_users_log   ON users;
DROP TRIGGER IF EXISTS trg_roles_log   ON roles;
DROP TRIGGER IF EXISTS trg_screens_log ON screens;

CREATE TRIGGER trg_users_log
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION fn_log_table_changes();

CREATE TRIGGER trg_roles_log
    AFTER INSERT OR UPDATE OR DELETE ON roles
    FOR EACH ROW EXECUTE FUNCTION fn_log_table_changes();

CREATE TRIGGER trg_screens_log
    AFTER INSERT OR UPDATE OR DELETE ON screens
    FOR EACH ROW EXECUTE FUNCTION fn_log_table_changes();

-- ---------------------------------------------------------------
-- PROCEDURE: Bir role ekran ata (veya mevcut yetkiyi güncelle)
-- ---------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_assign_screen_to_role(
    p_role_id    BIGINT,
    p_screen_id  BIGINT,
    p_can_create BOOLEAN DEFAULT true,
    p_can_read   BOOLEAN DEFAULT true,
    p_can_update BOOLEAN DEFAULT false,
    p_can_delete BOOLEAN DEFAULT false,
    p_file_types JSONB   DEFAULT '["txt","png","jpg","jpeg","pdf"]'::JSONB
)
LANGUAGE plpgsql AS $$
DECLARE
    v_permissions JSONB;
    v_new_perm    JSONB;
    v_exists      BOOLEAN := false;
    v_idx         INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM roles   WHERE id = p_role_id)  THEN
        RAISE EXCEPTION 'Role % bulunamadı', p_role_id;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM screens WHERE id = p_screen_id) THEN
        RAISE EXCEPTION 'Screen % bulunamadı', p_screen_id;
    END IF;

    SELECT COALESCE(value->'screen_permissions', '[]'::JSONB)
    INTO v_permissions FROM roles WHERE id = p_role_id;

    v_new_perm := jsonb_build_object(
        'screen_id',          p_screen_id,
        'can_create',         p_can_create,
        'can_read',           p_can_read,
        'can_update',         p_can_update,
        'can_delete',         p_can_delete,
        'allowed_file_types', p_file_types
    );

    FOR v_idx IN 0 .. jsonb_array_length(v_permissions) - 1 LOOP
        IF (v_permissions->v_idx->>'screen_id')::BIGINT = p_screen_id THEN
            v_exists      := true;
            v_permissions := jsonb_set(v_permissions, ARRAY[v_idx::TEXT], v_new_perm);
            EXIT;
        END IF;
    END LOOP;

    IF NOT v_exists THEN
        v_permissions := v_permissions || jsonb_build_array(v_new_perm);
    END IF;

    UPDATE roles
    SET value = jsonb_set(value, '{screen_permissions}', v_permissions)
    WHERE id = p_role_id;
END;
$$;

-- ---------------------------------------------------------------
-- PROCEDURE: Rolden ekran yetkisini kaldır
-- ---------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_remove_screen_from_role(
    p_role_id   BIGINT,
    p_screen_id BIGINT
)
LANGUAGE plpgsql AS $$
DECLARE
    v_permissions JSONB;
    v_filtered    JSONB;
BEGIN
    SELECT COALESCE(value->'screen_permissions', '[]'::JSONB)
    INTO v_permissions FROM roles WHERE id = p_role_id;

    SELECT jsonb_agg(elem)
    INTO v_filtered
    FROM jsonb_array_elements(v_permissions) AS elem
    WHERE (elem->>'screen_id')::BIGINT != p_screen_id;

    UPDATE roles
    SET value = jsonb_set(value, '{screen_permissions}', COALESCE(v_filtered, '[]'::JSONB))
    WHERE id = p_role_id;
END;
$$;

-- ---------------------------------------------------------------
-- FUNCTION: Kullanıcının erişebileceği ekranları getir
-- ---------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_get_user_screens(p_user_id BIGINT)
RETURNS JSONB LANGUAGE plpgsql AS $$
DECLARE
    v_role_id BIGINT;
    v_result  JSONB;
BEGIN
    SELECT (value->>'role_id')::BIGINT INTO v_role_id
    FROM users WHERE id = p_user_id;

    IF v_role_id IS NULL THEN RETURN '[]'::JSONB; END IF;

    SELECT jsonb_agg(
        s.value
        || jsonb_build_object('screen_id', s.id)
        || jsonb_build_object('permissions', perm)
    )
    INTO v_result
    FROM roles r,
         jsonb_array_elements(r.value->'screen_permissions') AS perm
         JOIN screens s ON s.id = (perm->>'screen_id')::BIGINT
    WHERE r.id = v_role_id
      AND (s.value->>'is_active')::BOOLEAN IS NOT FALSE;

    RETURN COALESCE(v_result, '[]'::JSONB);
END;
$$;
