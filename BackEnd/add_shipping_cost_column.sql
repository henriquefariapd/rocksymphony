-- Script para adicionar coluna shipping_cost na tabela orders
-- Execute este script no Supabase SQL Editor

ALTER TABLE orders ADD COLUMN IF NOT EXISTS shipping_cost DECIMAL(10,2) DEFAULT 0.00;

-- Atualizar descrição da tabela
COMMENT ON COLUMN orders.shipping_cost IS 'Valor do frete calculado para o pedido';
