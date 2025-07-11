-- Script para verificar e corrigir o usuário admin
-- Execute este script no Supabase SQL Editor

-- 1. Verificar se o usuário existe na tabela users
SELECT * FROM users WHERE id = 'da7266be-6651-4232-9bd0-b5f170d6801b';

-- 2. Se não existir, inserir o usuário admin
INSERT INTO users (id, usuario, is_admin, created_at) 
VALUES ('da7266be-6651-4232-9bd0-b5f170d6801b', 'admin', true, NOW())
ON CONFLICT (id) DO UPDATE SET 
    usuario = EXCLUDED.usuario,
    is_admin = EXCLUDED.is_admin;

-- 3. Verificar se foi inserido/atualizado
SELECT * FROM users WHERE id = 'da7266be-6651-4232-9bd0-b5f170d6801b';

-- 4. Verificar as políticas de RLS da tabela users
SELECT * FROM pg_policies WHERE tablename = 'users';

-- 5. Temporariamente, desabilitar RLS para teste (CUIDADO: só para desenvolvimento)
-- ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- 6. Para reabilitar depois:
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
