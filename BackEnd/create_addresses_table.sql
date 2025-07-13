-- Criar tabela de endereços
CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    cep VARCHAR(10) NOT NULL,
    street VARCHAR(255) NOT NULL,
    number VARCHAR(20) NOT NULL,
    complement VARCHAR(255),
    neighborhood VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(10) NOT NULL,
    country VARCHAR(50) DEFAULT 'Brasil',
    receiver_name VARCHAR(255) NOT NULL,
    full_address TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_addresses_user_id ON addresses(user_id);
CREATE INDEX IF NOT EXISTS idx_addresses_is_default ON addresses(user_id, is_default);

-- RLS (Row Level Security) para garantir que usuários só vejam seus próprios endereços
ALTER TABLE addresses ENABLE ROW LEVEL SECURITY;

-- Política para que usuários só vejam/editem seus próprios endereços
CREATE POLICY "Users can view own addresses" ON addresses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own addresses" ON addresses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own addresses" ON addresses
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own addresses" ON addresses
    FOR DELETE USING (auth.uid() = user_id);

-- Comentários das colunas
COMMENT ON TABLE addresses IS 'Endereços de entrega dos usuários';
COMMENT ON COLUMN addresses.user_id IS 'ID do usuário proprietário do endereço';
COMMENT ON COLUMN addresses.cep IS 'Código de Endereçamento Postal (CEP)';
COMMENT ON COLUMN addresses.street IS 'Nome da rua/avenida';
COMMENT ON COLUMN addresses.number IS 'Número do imóvel';
COMMENT ON COLUMN addresses.complement IS 'Complemento (apartamento, casa, etc.)';
COMMENT ON COLUMN addresses.neighborhood IS 'Bairro';
COMMENT ON COLUMN addresses.city IS 'Cidade';
COMMENT ON COLUMN addresses.state IS 'Estado (UF)';
COMMENT ON COLUMN addresses.country IS 'País';
COMMENT ON COLUMN addresses.receiver_name IS 'Nome da pessoa que irá receber';
COMMENT ON COLUMN addresses.full_address IS 'Endereço completo formatado';
COMMENT ON COLUMN addresses.is_default IS 'Se é o endereço padrão do usuário';
