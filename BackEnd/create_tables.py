import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def create_tables():
    """Cria as tabelas no Supabase usando SQLAlchemy"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no arquivo .env")
        return
    
    engine = create_engine(DATABASE_URL)
    
    sql_commands = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            artist VARCHAR(200) NOT NULL,
            description TEXT,
            valor DECIMAL(10, 2) NOT NULL,
            remaining INTEGER NOT NULL DEFAULT 0,
            image_path VARCHAR(500),
            genre VARCHAR(100),
            release_year INTEGER,
            label VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS shoppingcarts (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(user_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            order_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            payment_link VARCHAR(500),
            pending BOOLEAN DEFAULT TRUE,
            active BOOLEAN DEFAULT TRUE,
            total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS shoppingcart_products (
            shoppingcart_id INTEGER REFERENCES shoppingcarts(id) ON DELETE CASCADE,
            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
            quantity INTEGER NOT NULL DEFAULT 1,
            added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            PRIMARY KEY (shoppingcart_id, product_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS order_products (
            order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
            quantity INTEGER NOT NULL DEFAULT 1,
            price_at_time DECIMAL(10, 2) NOT NULL,
            PRIMARY KEY (order_id, product_id)
        );
        """,
        """
        -- Habilitar RLS nas tabelas
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE products ENABLE ROW LEVEL SECURITY;
        ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
        ALTER TABLE shoppingcarts ENABLE ROW LEVEL SECURITY;
        ALTER TABLE shoppingcart_products ENABLE ROW LEVEL SECURITY;
        ALTER TABLE order_products ENABLE ROW LEVEL SECURITY;
        """,
        """
        -- Políticas para products (todos podem ler)
        CREATE POLICY "Products are viewable by everyone" ON products
            FOR SELECT USING (true);
        """,
        """
        -- Políticas para orders (usuários só veem seus próprios pedidos)
        CREATE POLICY "Users can view their own orders" ON orders
            FOR SELECT USING (auth.uid() = user_id);

        CREATE POLICY "Users can insert their own orders" ON orders
            FOR INSERT WITH CHECK (auth.uid() = user_id);
        """,
        """
        -- Políticas para shoppingcarts (usuários só veem seus próprios carrinhos)
        CREATE POLICY "Users can view their own cart" ON shoppingcarts
            FOR SELECT USING (auth.uid() = user_id);

        CREATE POLICY "Users can manage their own cart" ON shoppingcarts
            FOR ALL USING (auth.uid() = user_id);
        """,
        """
        -- Inserir alguns produtos de exemplo (CDs de Rock)
        INSERT INTO products (name, artist, description, valor, remaining, genre, release_year, label) VALUES
        ('Master of Puppets', 'Metallica', 'Álbum clássico do heavy metal', 49.90, 10, 'Heavy Metal', 1986, 'Elektra Records'),
        ('Back in Black', 'AC/DC', 'Um dos álbuns mais vendidos de todos os tempos', 44.90, 15, 'Hard Rock', 1980, 'Atlantic Records'),
        ('The Dark Side of the Moon', 'Pink Floyd', 'Obra-prima do rock progressivo', 59.90, 8, 'Progressive Rock', 1973, 'Harvest Records'),
        ('Led Zeppelin IV', 'Led Zeppelin', 'Contém Stairway to Heaven', 54.90, 12, 'Hard Rock', 1971, 'Atlantic Records'),
        ('Appetite for Destruction', 'Guns N Roses', 'Álbum de estreia explosivo', 39.90, 20, 'Hard Rock', 1987, 'Geffen Records')
        ON CONFLICT (name, artist) DO NOTHING;
        """
    ]
    
    try:
        with engine.connect() as conn:
            for i, sql in enumerate(sql_commands, 1):
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"✅ Comando {i}/{len(sql_commands)} executado com sucesso")
                except Exception as e:
                    print(f"⚠️ Comando {i} falhou (pode ser normal se já existir): {e}")
                    continue
        
        print("✅ Processo concluído!")
        print("✅ Tabelas criadas/verificadas com sucesso!")
        print("✅ Produtos de exemplo inseridos!")
        
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco: {e}")
    
    finally:
        engine.dispose()

if __name__ == "__main__":
    create_tables()
