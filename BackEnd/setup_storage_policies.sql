-- CONFIGURAR POLÍTICAS DE STORAGE PARA PERMITIR UPLOADS
-- Execute no SQL Editor do Supabase

-- Primeiro, vamos remover políticas existentes se houver
DROP POLICY IF EXISTS "Allow public uploads to product-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow public access to product-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated users to upload product images" ON storage.objects;
DROP POLICY IF EXISTS "Allow public read access to product images" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated users to delete product images" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated users to update product images" ON storage.objects;

-- Criar políticas mais permissivas para o bucket product-images
-- Política para permitir upload de imagens (usuários autenticados)
CREATE POLICY "Allow authenticated users to upload product images" ON storage.objects
FOR INSERT TO authenticated
WITH CHECK (bucket_id = 'product-images');

-- Política para permitir leitura pública de imagens
CREATE POLICY "Allow public read access to product images" ON storage.objects
FOR SELECT TO public
USING (bucket_id = 'product-images');

-- Política para permitir exclusão de objetos no bucket product-images (para admins)
CREATE POLICY "Allow authenticated users to delete product images" ON storage.objects
FOR DELETE TO authenticated
USING (bucket_id = 'product-images');

-- Política para permitir atualização de objetos no bucket product-images
CREATE POLICY "Allow authenticated users to update product images" ON storage.objects
FOR UPDATE TO authenticated
USING (bucket_id = 'product-images');

-- Habilitar RLS se não estiver habilitado
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Política para permitir update de imagens
CREATE POLICY "Allow public update to product-images" ON storage.objects
  FOR UPDATE USING (bucket_id = 'product-images');

-- Política para permitir delete de imagens
CREATE POLICY "Allow public delete to product-images" ON storage.objects
  FOR DELETE USING (bucket_id = 'product-images');
