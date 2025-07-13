-- Corrigir políticas RLS para a tabela addresses
-- Execute este script no SQL Editor do Supabase

-- Primeiro, remover políticas existentes se houver problemas
DROP POLICY IF EXISTS "Users can view own addresses" ON addresses;
DROP POLICY IF EXISTS "Users can insert own addresses" ON addresses;
DROP POLICY IF EXISTS "Users can update own addresses" ON addresses;
DROP POLICY IF EXISTS "Users can delete own addresses" ON addresses;

-- Verificar se a tabela addresses existe, se não, criar
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

-- Habilitar RLS
ALTER TABLE addresses ENABLE ROW LEVEL SECURITY;

-- Criar políticas RLS mais permissivas
CREATE POLICY "Enable read access for users to own addresses" ON addresses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Enable insert access for authenticated users" ON addresses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable update access for users to own addresses" ON addresses
    FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable delete access for users to own addresses" ON addresses
    FOR DELETE USING (auth.uid() = user_id);

-- Garantir que o usuário autenticado pode acessar a tabela
GRANT ALL ON addresses TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE addresses_id_seq TO authenticated;

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_addresses_user_id ON addresses(user_id);
CREATE INDEX IF NOT EXISTS idx_addresses_is_default ON addresses(user_id, is_default);

-- Comentários
COMMENT ON TABLE addresses IS 'Endereços de entrega dos usuários';
COMMENT ON COLUMN addresses.user_id IS 'ID do usuário proprietário do endereço';
COMMENT ON COLUMN addresses.full_address IS 'Endereço completo formatado';
COMMENT ON COLUMN addresses.is_default IS 'Se é o endereço padrão do usuário';
