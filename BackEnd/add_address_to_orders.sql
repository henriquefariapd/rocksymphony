-- Adicionar coluna address_id na tabela orders
-- Execute este script no SQL Editor do Supabase

-- Verificar se a coluna já existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'orders' 
        AND column_name = 'address_id'
    ) THEN
        -- Adicionar a coluna address_id
        ALTER TABLE orders 
        ADD COLUMN address_id INTEGER REFERENCES addresses(id);
        
        -- Criar índice para melhor performance
        CREATE INDEX IF NOT EXISTS idx_orders_address_id ON orders(address_id);
        
        -- Comentário
        COMMENT ON COLUMN orders.address_id IS 'ID do endereço de entrega do pedido';
    END IF;
END $$;
