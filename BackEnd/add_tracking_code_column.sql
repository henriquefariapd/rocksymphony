-- Adicionar coluna tracking_code na tabela orders
ALTER TABLE orders 
ADD COLUMN tracking_code VARCHAR(255);

-- Comentário explicativo sobre a coluna
COMMENT ON COLUMN orders.tracking_code IS 'Código de rastreamento dos correios para o pedido';
