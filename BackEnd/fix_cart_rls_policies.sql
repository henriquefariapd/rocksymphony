-- VERIFICAR E CORRIGIR POLÍTICAS RLS PARA CARRINHO
-- Execute no SQL Editor do Supabase

-- Verificar políticas existentes
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies 
WHERE tablename IN ('shoppingcarts', 'shoppingcart_products');

-- Se não houver políticas ou estiverem restritivas, executar:

-- Remover políticas existentes se houver
DROP POLICY IF EXISTS "Users can manage their own shopping carts" ON shoppingcarts;
DROP POLICY IF EXISTS "Users can manage their own cart products" ON shoppingcart_products;

-- Criar políticas mais permissivas para carrinho
CREATE POLICY "Allow authenticated users to manage shopping carts" ON shoppingcarts
FOR ALL TO authenticated
USING (true)
WITH CHECK (true);

CREATE POLICY "Allow authenticated users to manage cart products" ON shoppingcart_products
FOR ALL TO authenticated
USING (true)
WITH CHECK (true);

-- Habilitar RLS se não estiver habilitado
ALTER TABLE shoppingcarts ENABLE ROW LEVEL SECURITY;
ALTER TABLE shoppingcart_products ENABLE ROW LEVEL SECURITY;

-- Verificar se as tabelas existem e têm dados
SELECT 'shoppingcarts' as table_name, count(*) as record_count FROM shoppingcarts
UNION ALL
SELECT 'shoppingcart_products' as table_name, count(*) as record_count FROM shoppingcart_products;
