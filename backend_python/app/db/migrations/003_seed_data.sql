-- =============================================================
-- Migration 003: Örnek / seed veriler
-- Varsayılan Supervisor şifresi: Admin123!
-- NOT: Üretimde password_hash bcrypt ile güncellenecek.
-- =============================================================

-- ---------------------------------------------------------------
-- Ekranlar (Screens)
-- ---------------------------------------------------------------
INSERT INTO screens (value) VALUES
  ('{"name":"dashboard","label":"Gösterge Paneli","path":"/dashboard","component":"DashboardPage","icon":"LayoutDashboard","description":"Ana gösterge paneli","is_active":true,"order":1}'),
  ('{"name":"student_list","label":"Öğrenci Listesi","path":"/students","component":"StudentListPage","icon":"GraduationCap","description":"Öğrenci listesi ve yönetimi","is_active":true,"order":2}'),
  ('{"name":"school_list","label":"Okul Listesi","path":"/schools","component":"SchoolListPage","icon":"Building2","description":"Okul listesi ve yönetimi","is_active":true,"order":3}'),
  ('{"name":"business_list","label":"İşletme Listesi","path":"/businesses","component":"BusinessListPage","icon":"Briefcase","description":"İşletme listesi ve yönetimi","is_active":true,"order":4}'),
  ('{"name":"file_manager","label":"Dosya Yöneticisi","path":"/files","component":"FileManagerPage","icon":"FolderOpen","description":"Dosya yükleme ve YZ analizi","is_active":true,"order":5}'),
  ('{"name":"user_management","label":"Kullanıcı Yönetimi","path":"/users","component":"UserManagementPage","icon":"Users","description":"Kullanıcı oluşturma ve yönetimi","is_active":true,"order":6}'),
  ('{"name":"role_management","label":"Rol Yönetimi","path":"/roles","component":"RoleManagementPage","icon":"Shield","description":"Rol ve yetki yönetimi","is_active":true,"order":7}'),
  ('{"name":"screen_management","label":"Ekran Yönetimi","path":"/screens","component":"ScreenManagementPage","icon":"Monitor","description":"Ekran ve erişim yönetimi","is_active":true,"order":8}'),
  ('{"name":"ai_assistant","label":"YZ Asistanı","path":"/ai","component":"AIAssistantPage","icon":"BrainCircuit","description":"Yapay zeka ile dosya analizi","is_active":true,"order":9}'),
  ('{"name":"logs_viewer","label":"Sistem Logları","path":"/logs","component":"LogsViewerPage","icon":"FileText","description":"Denetim ve aktivite logları","is_active":true,"order":10}')
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------
-- Roller (Roles) — screen_permissions procedure ile sonra doldurulur
-- ---------------------------------------------------------------
INSERT INTO roles (value) VALUES
  ('{"name":"supervisor","label":"Süpervizör","group_type":"supervisor","is_active":true,"screen_permissions":[]}'),
  ('{"name":"student","label":"Öğrenci","group_type":"student","is_active":true,"screen_permissions":[]}'),
  ('{"name":"school","label":"Okul","group_type":"school","is_active":true,"screen_permissions":[]}'),
  ('{"name":"business","label":"İşletme","group_type":"business","is_active":true,"screen_permissions":[]}')
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------
-- Supervisor rolüne tüm ekranları ata (tam yetki)
-- ---------------------------------------------------------------
DO $$
DECLARE
    v_supervisor_role_id BIGINT;
    v_screen             RECORD;
BEGIN
    SELECT id INTO v_supervisor_role_id FROM roles WHERE value->>'name' = 'supervisor' LIMIT 1;

    FOR v_screen IN SELECT id FROM screens LOOP
        CALL sp_assign_screen_to_role(
            v_supervisor_role_id,
            v_screen.id,
            true, true, true, true,
            '["txt","png","jpg","jpeg","pdf","word","excel"]'::JSONB
        );
    END LOOP;
END;
$$;

-- Öğrenci rolüne: dashboard, student_list, file_manager, ai_assistant
DO $$
DECLARE
    v_role_id  BIGINT;
    v_screen_id BIGINT;
BEGIN
    SELECT id INTO v_role_id FROM roles WHERE value->>'name' = 'student' LIMIT 1;

    SELECT id INTO v_screen_id FROM screens WHERE value->>'name' = 'dashboard';
    CALL sp_assign_screen_to_role(v_role_id, v_screen_id, false, true, false, false, '[]'::JSONB);

    SELECT id INTO v_screen_id FROM screens WHERE value->>'name' = 'student_list';
    CALL sp_assign_screen_to_role(v_role_id, v_screen_id, false, true, false, false, '[]'::JSONB);

    SELECT id INTO v_screen_id FROM screens WHERE value->>'name' = 'file_manager';
    CALL sp_assign_screen_to_role(v_role_id, v_screen_id, true, true, false, false,
        '["txt","png","jpg","jpeg","pdf"]'::JSONB);

    SELECT id INTO v_screen_id FROM screens WHERE value->>'name' = 'ai_assistant';
    CALL sp_assign_screen_to_role(v_role_id, v_screen_id, false, true, false, false, '[]'::JSONB);
END;
$$;

-- Okul rolüne: dashboard, school_list, student_list, file_manager, ai_assistant
DO $$
DECLARE
    v_role_id   BIGINT;
    v_screen_id BIGINT;
BEGIN
    SELECT id INTO v_role_id FROM roles WHERE value->>'name' = 'school' LIMIT 1;

    FOREACH v_screen_id IN ARRAY ARRAY(
        SELECT id FROM screens
        WHERE value->>'name' IN ('dashboard','school_list','student_list','file_manager','ai_assistant')
    ) LOOP
        CALL sp_assign_screen_to_role(v_role_id, v_screen_id, true, true, true, false,
            '["txt","png","jpg","jpeg","pdf","word","excel"]'::JSONB);
    END LOOP;
END;
$$;

-- İşletme rolüne: dashboard, business_list, file_manager, ai_assistant
DO $$
DECLARE
    v_role_id   BIGINT;
    v_screen_id BIGINT;
BEGIN
    SELECT id INTO v_role_id FROM roles WHERE value->>'name' = 'business' LIMIT 1;

    FOREACH v_screen_id IN ARRAY ARRAY(
        SELECT id FROM screens
        WHERE value->>'name' IN ('dashboard','business_list','file_manager','ai_assistant')
    ) LOOP
        CALL sp_assign_screen_to_role(v_role_id, v_screen_id, true, true, true, false,
            '["txt","png","jpg","jpeg","pdf","word","excel"]'::JSONB);
    END LOOP;
END;
$$;

-- ---------------------------------------------------------------
-- Varsayılan kullanıcılar
-- Şifre: Admin123! → hash placeholder (bcrypt ile güncellenecek)
-- ---------------------------------------------------------------
INSERT INTO users (group_type, value)
SELECT 'supervisor', jsonb_build_object(
    'email',         'admin@akilliatolye.com',
    'password_hash', '$2b$12$PLACEHOLDER_REPLACE_WITH_BCRYPT',
    'name',          'Admin',
    'surname',       'Süpervizör',
    'role_id',       (SELECT id FROM roles WHERE value->>'name' = 'supervisor' LIMIT 1),
    'is_active',     true,
    'avatar_url',    null,
    'last_login',    null,
    'phone',         null
)
WHERE NOT EXISTS (SELECT 1 FROM users WHERE value->>'email' = 'admin@akilliatolye.com');

INSERT INTO users (group_type, value)
SELECT 'student', jsonb_build_object(
    'email',         'ogrenci@akilliatolye.com',
    'password_hash', '$2b$12$PLACEHOLDER_REPLACE_WITH_BCRYPT',
    'name',          'Ahmet',
    'surname',       'Yılmaz',
    'role_id',       (SELECT id FROM roles WHERE value->>'name' = 'student' LIMIT 1),
    'is_active',     true,
    'avatar_url',    null,
    'last_login',    null,
    'phone',         null
)
WHERE NOT EXISTS (SELECT 1 FROM users WHERE value->>'email' = 'ogrenci@akilliatolye.com');

INSERT INTO users (group_type, value)
SELECT 'school', jsonb_build_object(
    'email',         'okul@akilliatolye.com',
    'password_hash', '$2b$12$PLACEHOLDER_REPLACE_WITH_BCRYPT',
    'name',          'Marmara',
    'surname',       'Üniversitesi',
    'role_id',       (SELECT id FROM roles WHERE value->>'name' = 'school' LIMIT 1),
    'is_active',     true,
    'avatar_url',    null,
    'last_login',    null,
    'phone',         null
)
WHERE NOT EXISTS (SELECT 1 FROM users WHERE value->>'email' = 'okul@akilliatolye.com');

INSERT INTO users (group_type, value)
SELECT 'business', jsonb_build_object(
    'email',         'isletme@akilliatolye.com',
    'password_hash', '$2b$12$PLACEHOLDER_REPLACE_WITH_BCRYPT',
    'name',          'AkilliTech',
    'surname',       'Ltd. Şti.',
    'role_id',       (SELECT id FROM roles WHERE value->>'name' = 'business' LIMIT 1),
    'is_active',     true,
    'avatar_url',    null,
    'last_login',    null,
    'phone',         null
)
WHERE NOT EXISTS (SELECT 1 FROM users WHERE value->>'email' = 'isletme@akilliatolye.com');
