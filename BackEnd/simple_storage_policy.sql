-- SCRIPT ALTERNATIVO MAIS SIMPLES
-- Se o script principal não funcionar, tente este:

-- Criar política mais permissiva para PUBLIC
CREATE POLICY "Public access to product images" ON storage.objects
FOR ALL TO public
USING (bucket_id = 'product-images')
WITH CHECK (bucket_id = 'product-images');

-- OU se ainda não funcionar, tente desabilitar RLS com service_role
-- (Você precisa executar este comando como service_role no SQL Editor)
-- ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;
