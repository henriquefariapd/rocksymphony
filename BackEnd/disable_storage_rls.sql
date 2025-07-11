-- DESABILITAR RLS TEMPORARIAMENTE PARA STORAGE
-- Execute no SQL Editor do Supabase para permitir uploads

-- Desabilitar RLS para storage.objects
ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;

-- Desabilitar RLS para storage.buckets  
ALTER TABLE storage.buckets DISABLE ROW LEVEL SECURITY;
