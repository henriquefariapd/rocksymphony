-- REVERTER POLÍTICAS RLS RESTRITIVAS E DEIXAR CARRINHO FUNCIONANDO
-- Execute no SQL Editor do Supabase

-- OPÇÃO 1: Desabilitar RLS completamente para carrinho (mais simples)
ALTER TABLE shoppingcarts DISABLE ROW LEVEL SECURITY;
ALTER TABLE shoppingcart_products DISABLE ROW LEVEL SECURITY;

-- OPÇÃO 2: Se não conseguir desabilitar, remover todas as políticas restritivas
DROP POLICY IF EXISTS "Allow authenticated users to manage shopping carts" ON shoppingcarts;
DROP POLICY IF EXISTS "Allow authenticated users to manage cart products" ON shoppingcart_products;
DROP POLICY IF EXISTS "Users can manage their own shopping carts" ON shoppingcarts;
DROP POLICY IF EXISTS "Users can manage their own cart products" ON shoppingcart_products;

-- OPÇÃO 3: Criar política super permissiva (se as anteriores não funcionarem)
CREATE POLICY "Allow all operations on shopping carts" ON shoppingcarts
FOR ALL TO public
USING (true)
WITH CHECK (true);

CREATE POLICY "Allow all operations on cart products" ON shoppingcart_products
FOR ALL TO public
USING (true)
WITH CHECK (true);

-- Verificar se as tabelas existem e têm dados
SELECT 'shoppingcarts' as table_name, count(*) as record_count FROM shoppingcarts
UNION ALL
SELECT 'shoppingcart_products' as table_name, count(*) as record_count FROM shoppingcart_products;
