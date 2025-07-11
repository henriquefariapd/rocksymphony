-- Script para desabilitar temporariamente o RLS da tabela users
-- Execute este script no Supabase SQL Editor

-- Desabilitar RLS temporariamente para teste
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- Para reabilitar depois (execute quando quiser reativar a segurança):
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
