-- Criar tabela de artistas
CREATE TABLE IF NOT EXISTS artists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    origin_country VARCHAR(100) NOT NULL,
    members TEXT,
    formed_year INTEGER,
    description TEXT,
    genre VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Adicionar coluna artist_id na tabela products
ALTER TABLE products ADD COLUMN IF NOT EXISTS artist_id INTEGER REFERENCES artists(id);

-- Remover a coluna artist antiga (se existir)
-- ALTER TABLE products DROP COLUMN IF EXISTS artist;

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_artists_origin_country ON artists(origin_country);
CREATE INDEX IF NOT EXISTS idx_products_artist_id ON products(artist_id);

-- Inserir alguns artistas exemplo baseados no progBandsByCountry
INSERT INTO artists (name, origin_country, members, formed_year, description, genre) VALUES
('Dream Theater', 'United States', 'James LaBrie, John Petrucci, Jordan Rudess, John Myung, Mike Mangini', 1985, 'Metal progressivo com virtuosismo técnico', 'Progressive Metal'),
('Tool', 'United States', 'Maynard James Keenan, Adam Jones, Justin Chancellor, Danny Carey', 1990, 'Progressive metal com elementos alternativos', 'Progressive Metal'),
('Pink Floyd', 'United Kingdom', 'David Gilmour, Roger Waters, Nick Mason, Richard Wright', 1965, 'Lendas do rock progressivo atmosférico', 'Progressive Rock'),
('Yes', 'United Kingdom', 'Jon Anderson, Steve Howe, Rick Wakeman, Chris Squire, Bill Bruford', 1968, 'Virtuosismo e complexidade melódica', 'Progressive Rock'),
('Rush', 'Canada', 'Geddy Lee, Alex Lifeson, Neil Peart', 1968, 'Trio virtuoso com letras filosóficas', 'Progressive Rock'),
('Opeth', 'Sweden', 'Mikael Åkerfeldt, Fredrik Åkesson, Martin Mendez, Martin Axenrot', 1990, 'Death metal progressivo melódico', 'Progressive Death Metal'),
('Angra', 'Brazil', 'Fabio Lione, Rafael Bittencourt, Felipe Andreoli, Aquiles Priester', 1991, 'Power metal progressivo brasileiro', 'Progressive Power Metal'),
('King Crimson', 'United Kingdom', 'Robert Fripp, Adrian Belew, Tony Levin, Pat Mastelotto', 1968, 'Experimentalismo e inovação constante', 'Progressive Rock'),
('Genesis', 'United Kingdom', 'Phil Collins, Tony Banks, Mike Rutherford', 1967, 'Evolução do prog teatral ao pop', 'Progressive Rock'),
('Porcupine Tree', 'United Kingdom', 'Steven Wilson, Richard Barbieri, Gavin Harrison, Colin Edwin', 1987, 'Progressive rock moderno', 'Progressive Rock'),
('Leprous', 'Norway', 'Einar Solberg, Tor Oddmund Suhrke, Simen Børven, Baard Kolstad', 2001, 'Progressive metal moderno', 'Progressive Metal'),
('Amorphis', 'Finland', 'Tomi Joutsen, Esa Holopainen, Tomi Koivusaari, Niclas Etelävuori', 1990, 'Progressive death/folk metal', 'Progressive Death Metal');
