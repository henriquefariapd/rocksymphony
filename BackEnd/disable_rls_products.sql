-- Script para desabilitar temporariamente o RLS da tabela products
-- Execute este script no Supabase SQL Editor

-- Desabilitar RLS temporariamente para teste
ALTER TABLE products DISABLE ROW LEVEL SECURITY;

-- Para reabilitar depois (execute quando quiser reativar a segurança):
-- ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Verificar se foi desabilitado
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename IN ('products', 'users');
