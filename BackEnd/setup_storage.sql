-- Script para configurar o bucket de imagens no Supabase Storage
-- Execute este script no Supabase SQL Editor

-- 1. Verificar se o bucket já existe
SELECT * FROM storage.buckets WHERE id = 'product-images';

-- 2. Criar o bucket para imagens de produtos (se não existir)
INSERT INTO storage.buckets (id, name, public, avif_autodetection, file_size_limit, allowed_mime_types)
VALUES ('product-images', 'product-images', true, false, 10485760, '{"image/jpeg","image/png","image/gif","image/webp","image/jpg"}')
ON CONFLICT (id) DO UPDATE SET 
    public = EXCLUDED.public,
    file_size_limit = EXCLUDED.file_size_limit,
    allowed_mime_types = EXCLUDED.allowed_mime_types;

-- 3. Remover políticas existentes
DROP POLICY IF EXISTS "Public Access" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated users can upload images" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated users can update images" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated users can delete images" ON storage.objects;

-- 4. Criar políticas mais permissivas
-- Permitir que todos vejam as imagens (leitura pública)
CREATE POLICY "Allow public read access to product images" ON storage.objects
FOR SELECT USING (bucket_id = 'product-images');

-- Permitir que usuários autenticados façam upload
CREATE POLICY "Allow authenticated users to upload product images" ON storage.objects
FOR INSERT WITH CHECK (
    bucket_id = 'product-images' 
    AND auth.uid() IS NOT NULL
);

-- Permitir que usuários autenticados atualizem
CREATE POLICY "Allow authenticated users to update product images" ON storage.objects
FOR UPDATE USING (
    bucket_id = 'product-images' 
    AND auth.uid() IS NOT NULL
);

-- Permitir que usuários autenticados deletem
CREATE POLICY "Allow authenticated users to delete product images" ON storage.objects
FOR DELETE USING (
    bucket_id = 'product-images' 
    AND auth.uid() IS NOT NULL
);

-- 5. Verificar se foi criado
SELECT * FROM storage.buckets WHERE id = 'product-images';
SELECT * FROM pg_policies WHERE tablename = 'objects' AND schemaname = 'storage';
