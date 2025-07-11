-- Script para verificar e criar tabelas de carrinho no Supabase
-- Execute no SQL Editor do Supabase

-- Verificar se as tabelas existem
SELECT 
    table_name,
    table_schema
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('shoppingcarts', 'shoppingcart_products');

-- Se as tabelas não existirem, criar:

-- Criar tabela de carrinho de compras
CREATE TABLE IF NOT EXISTS public.shoppingcarts (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Criar tabela de produtos no carrinho
CREATE TABLE IF NOT EXISTS public.shoppingcart_products (
    shoppingcart_id INTEGER NOT NULL REFERENCES public.shoppingcarts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (shoppingcart_id, product_id)
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_shoppingcarts_user_id ON public.shoppingcarts(user_id);
CREATE INDEX IF NOT EXISTS idx_shoppingcart_products_cart_id ON public.shoppingcart_products(shoppingcart_id);
CREATE INDEX IF NOT EXISTS idx_shoppingcart_products_product_id ON public.shoppingcart_products(product_id);

-- Desabilitar RLS temporariamente para desenvolvimento
ALTER TABLE public.shoppingcarts DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.shoppingcart_products DISABLE ROW LEVEL SECURITY;

-- Verificar se as tabelas foram criadas
SELECT 
    table_name,
    table_schema
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('shoppingcarts', 'shoppingcart_products');

-- Verificar se RLS está desabilitado
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('shoppingcarts', 'shoppingcart_products');

-- Inserir dados de teste (opcional)
-- INSERT INTO public.shoppingcarts (user_id) VALUES ('da7266be-6651-4232-9bd0-b5f170d6801b');

-- Comentários nas tabelas
COMMENT ON TABLE public.shoppingcarts IS 'Carrinho de compras dos usuários';
COMMENT ON TABLE public.shoppingcart_products IS 'Produtos no carrinho de compras';
