-- Criar enum para países
CREATE TYPE country_enum AS ENUM (
  'Brasil',
  'Estados Unidos',
  'Reino Unido',
  'Alemanha',
  'França',
  'Japão',
  'Canadá',
  'Austrália',
  'Argentina',
  'México',
  'Holanda',
  'Suécia',
  'Noruega',
  'Dinamarca',
  'Finlândia',
  'Itália',
  'Espanha',
  'Portugal',
  'Bélgica',
  'Áustria',
  'Suíça',
  'Polônia',
  'República Tcheca',
  'Hungria',
  'Grécia',
  'Turquia',
  'Rússia',
  'China',
  'Coreia do Sul',
  'Índia',
  'Tailândia',
  'Singapura',
  'Nova Zelândia',
  'África do Sul',
  'Chile',
  'Colômbia',
  'Peru',
  'Uruguai',
  'Paraguai',
  'Bolívia',
  'Equador',
  'Venezuela',
  'Cuba',
  'Jamaica',
  'Outro'
);

-- Adicionar novos campos na tabela products
ALTER TABLE products 
ADD COLUMN reference_code VARCHAR(100),
ADD COLUMN stamp VARCHAR(100),
ADD COLUMN country country_enum;

-- Verificar se a coluna release_year já existe (ela já está no modelo)
-- Se não existir, descomente a linha abaixo:
-- ALTER TABLE products ADD COLUMN release_year INTEGER;

-- Comentários para documentar os novos campos
COMMENT ON COLUMN products.reference_code IS 'Código de referência do produto';
COMMENT ON COLUMN products.stamp IS 'Selo do produto';  
COMMENT ON COLUMN products.country IS 'País de origem (não aparece na listagem)';
