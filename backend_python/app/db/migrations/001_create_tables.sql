-- =============================================================
-- Migration 001: Temel tablolar (JSONB-first şema)
-- =============================================================

-- Gerekli eklentiler
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grup tipi enum
DO $$ BEGIN
    CREATE TYPE group_type_enum AS ENUM ('supervisor', 'student', 'school', 'business');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ---------------------------------------------------------------
-- screens: Uygulamadaki ekranlar / sayfalar
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS screens (
    id         BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- value içeriği: name, label, path, component, icon, description, is_active, order
    value      JSONB NOT NULL DEFAULT '{}'
);

-- ---------------------------------------------------------------
-- roles: Roller ve ekran/CRUD yetkileri
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id         BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- value içeriği: name, label, group_type, is_active,
    --   screen_permissions: [{screen_id, can_create, can_read,
    --     can_update, can_delete, allowed_file_types[]}]
    value      JSONB NOT NULL DEFAULT '{}'
);

-- ---------------------------------------------------------------
-- users: Kullanıcılar
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id         BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    group_type group_type_enum NOT NULL DEFAULT 'student',
    -- value içeriği: email, password_hash, name, surname,
    --   role_id, is_active, avatar_url, last_login, phone
    value      JSONB NOT NULL DEFAULT '{}'
);

-- ---------------------------------------------------------------
-- logs: Değişmez denetim kayıtları (immutable audit log)
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS logs (
    id         BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- value içeriği: user_id, action, table_name, record_id,
    --   old_value, new_value, ip_address, user_agent,
    --   status, message, rabbitmq_published
    value      JSONB NOT NULL DEFAULT '{}'
);

-- ---------------------------------------------------------------
-- İndeksler
-- ---------------------------------------------------------------
-- users
CREATE INDEX IF NOT EXISTS idx_users_email      ON users ((value->>'email'));
CREATE INDEX IF NOT EXISTS idx_users_role_id    ON users ((value->>'role_id'));
CREATE INDEX IF NOT EXISTS idx_users_group_type ON users (group_type);
CREATE INDEX IF NOT EXISTS idx_users_is_active  ON users ((value->>'is_active'));
CREATE INDEX IF NOT EXISTS idx_users_gin        ON users USING GIN (value);

-- roles
CREATE INDEX IF NOT EXISTS idx_roles_name       ON roles ((value->>'name'));
CREATE INDEX IF NOT EXISTS idx_roles_group_type ON roles ((value->>'group_type'));
CREATE INDEX IF NOT EXISTS idx_roles_gin        ON roles USING GIN (value);

-- screens
CREATE INDEX IF NOT EXISTS idx_screens_name     ON screens ((value->>'name'));
CREATE INDEX IF NOT EXISTS idx_screens_path     ON screens ((value->>'path'));
CREATE INDEX IF NOT EXISTS idx_screens_active   ON screens ((value->>'is_active'));

-- logs
CREATE INDEX IF NOT EXISTS idx_logs_action      ON logs ((value->>'action'));
CREATE INDEX IF NOT EXISTS idx_logs_table       ON logs ((value->>'table_name'));
CREATE INDEX IF NOT EXISTS idx_logs_user_id     ON logs ((value->>'user_id'));
CREATE INDEX IF NOT EXISTS idx_logs_record_id   ON logs ((value->>'record_id'));
CREATE INDEX IF NOT EXISTS idx_logs_created_at  ON logs (created_at);
CREATE INDEX IF NOT EXISTS idx_logs_gin         ON logs USING GIN (value);
