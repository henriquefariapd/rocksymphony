-- Script para corrigir as políticas de segurança da tabela users
-- Execute este script no Supabase SQL Editor

-- Primeiro, vamos ver as políticas atuais
SELECT * FROM pg_policies WHERE tablename = 'users';

-- Remover políticas existentes se houver
DROP POLICY IF EXISTS "Users can view own data" ON users;
DROP POLICY IF EXISTS "Users can insert own data" ON users;
DROP POLICY IF EXISTS "Users can update own data" ON users;
DROP POLICY IF EXISTS "Enable read access for all users" ON users;
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON users;
DROP POLICY IF EXISTS "Enable update for users based on email" ON users;

-- Criar políticas mais permissivas para a tabela users
CREATE POLICY "Allow authenticated users to insert their own data" ON users
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Allow authenticated users to view their own data" ON users
    FOR SELECT
    TO authenticated
    USING (auth.uid() = id);

CREATE POLICY "Allow authenticated users to update their own data" ON users
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Permitir que o service role faça qualquer operação (para o backend)
CREATE POLICY "Allow service role full access" ON users
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Verificar se RLS está habilitado
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'users' AND schemaname = 'public';

-- Se necessário, habilitar RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Mostrar as políticas criadas
SELECT * FROM pg_policies WHERE tablename = 'users';
