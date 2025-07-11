-- Script para corrigir as políticas de RLS (Row Level Security) da tabela users
-- Execute este script no Supabase SQL Editor

-- 1. Remover políticas existentes que possam estar causando problema
DROP POLICY IF EXISTS "Users can view own data" ON users;
DROP POLICY IF EXISTS "Users can insert own data" ON users;
DROP POLICY IF EXISTS "Users can update own data" ON users;
DROP POLICY IF EXISTS "Enable read access for all users" ON users;
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON users;
DROP POLICY IF EXISTS "Enable update for users based on email" ON users;

-- 2. Criar políticas mais permissivas para autenticação
-- Permitir que usuários autenticados leiam seus próprios dados
CREATE POLICY "Users can read own data" ON users
    FOR SELECT 
    USING (auth.uid() = id);

-- Permitir que usuários autenticados insiram seus próprios dados
CREATE POLICY "Users can insert own data" ON users
    FOR INSERT 
    WITH CHECK (auth.uid() = id);

-- Permitir que usuários autenticados atualizem seus próprios dados
CREATE POLICY "Users can update own data" ON users
    FOR UPDATE 
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- 3. Verificar se RLS está habilitado (deve estar)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 4. Verificar se as políticas foram criadas corretamente
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'users';
