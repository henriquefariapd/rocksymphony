-- Script para desabilitar RLS temporariamente nas tabelas de carrinho
-- Execute no SQL Editor do Supabase

-- Desabilitar RLS nas tabelas de carrinho
ALTER TABLE public.shoppingcarts DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.shoppingcart_products DISABLE ROW LEVEL SECURITY;

-- Verificar se as tabelas existem e têm RLS desabilitado
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('shoppingcarts', 'shoppingcart_products');

-- Resultado esperado: rowsecurity = false para ambas as tabelas

-- Comentário: 
-- Este script desabilita temporariamente o RLS para desenvolvimento
-- Em produção, você deve configurar políticas RLS adequadas
-- Para reabilitar: ALTER TABLE public.shoppingcarts ENABLE ROW LEVEL SECURITY;
