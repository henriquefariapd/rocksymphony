-- VERSÃO TEMPORÁRIA - Políticas mais permissivas para teste
-- Execute este script APENAS se o anterior não funcionar

-- 1. Desabilitar temporariamente o RLS para teste
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- Para reabilitar depois (execute após confirmar que funciona):
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
