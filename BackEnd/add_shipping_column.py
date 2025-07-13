# Script Python para adicionar a coluna shipping_cost na tabela orders
# Execute este script para atualizar a estrutura da tabela

try:
    # Tentativa para Heroku (import relativo)
    from .models import SessionLocal, engine
    from .supabase_client import supabase
except ImportError:
    # Fallback para desenvolvimento local (import absoluto)
    from models import SessionLocal, engine
    from supabase_client import supabase

def add_shipping_cost_column():
    """Adiciona a coluna shipping_cost na tabela orders"""
    try:
        # Para Supabase (PostgreSQL), execute este SQL no SQL Editor:
        sql_query = """
        ALTER TABLE orders ADD COLUMN IF NOT EXISTS shipping_cost DECIMAL(10,2) DEFAULT 0.00;
        COMMENT ON COLUMN orders.shipping_cost IS 'Valor do frete calculado para o pedido';
        """
        
        print("Execute o seguinte SQL no Supabase SQL Editor:")
        print(sql_query)
        print("\nOu execute este script Python se estiver usando SQLAlchemy diretamente:")
        
        # Para SQLAlchemy local (SQLite/PostgreSQL)
        from sqlalchemy import text
        
        with engine.connect() as connection:
            # Verificar se a coluna já existe
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'orders' AND column_name = 'shipping_cost'
            """))
            
            if not result.fetchone():
                # Adicionar a coluna se não existir
                connection.execute(text("""
                    ALTER TABLE orders ADD COLUMN shipping_cost DECIMAL(10,2) DEFAULT 0.00
                """))
                connection.commit()
                print("Coluna shipping_cost adicionada com sucesso!")
            else:
                print("Coluna shipping_cost já existe na tabela orders.")
                
    except Exception as e:
        print(f"Erro ao adicionar coluna: {e}")
        print("Para PostgreSQL/Supabase, execute manualmente no SQL Editor:")
        print("ALTER TABLE orders ADD COLUMN IF NOT EXISTS shipping_cost DECIMAL(10,2) DEFAULT 0.00;")

if __name__ == "__main__":
    add_shipping_cost_column()
