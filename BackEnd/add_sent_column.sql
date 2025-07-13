-- Adicionar coluna 'sent' à tabela orders
ALTER TABLE orders ADD COLUMN IF NOT EXISTS sent BOOLEAN DEFAULT FALSE;

-- Atualizar RLS policies se necessário
-- A coluna sent seguirá as mesmas políticas já existentes para a tabela orders
