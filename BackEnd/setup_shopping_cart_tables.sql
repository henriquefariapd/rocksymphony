-- Script para criar as tabelas de carrinho no Supabase
-- Executar no SQL Editor do Supabase

-- Criar tabela de carrinho de compras
CREATE TABLE IF NOT EXISTS public.shoppingcarts (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Criar tabela de produtos no carrinho
CREATE TABLE IF NOT EXISTS public.shoppingcart_products (
    shoppingcart_id INTEGER NOT NULL REFERENCES public.shoppingcarts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (shoppingcart_id, product_id)
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_shoppingcarts_user_id ON public.shoppingcarts(user_id);
CREATE INDEX IF NOT EXISTS idx_shoppingcart_products_cart_id ON public.shoppingcart_products(shoppingcart_id);
CREATE INDEX IF NOT EXISTS idx_shoppingcart_products_product_id ON public.shoppingcart_products(product_id);

-- Configurar RLS (Row Level Security)
ALTER TABLE public.shoppingcarts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shoppingcart_products ENABLE ROW LEVEL SECURITY;

-- Política para shoppingcarts: usuários podem ver apenas seus próprios carrinhos
CREATE POLICY "Users can view their own shopping carts" ON public.shoppingcarts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own shopping carts" ON public.shoppingcarts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own shopping carts" ON public.shoppingcarts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own shopping carts" ON public.shoppingcarts
    FOR DELETE USING (auth.uid() = user_id);

-- Política para shoppingcart_products: usuários podem ver apenas produtos dos seus carrinhos
CREATE POLICY "Users can view products in their own shopping carts" ON public.shoppingcart_products
    FOR SELECT USING (
        shoppingcart_id IN (
            SELECT id FROM public.shoppingcarts WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert products in their own shopping carts" ON public.shoppingcart_products
    FOR INSERT WITH CHECK (
        shoppingcart_id IN (
            SELECT id FROM public.shoppingcarts WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update products in their own shopping carts" ON public.shoppingcart_products
    FOR UPDATE USING (
        shoppingcart_id IN (
            SELECT id FROM public.shoppingcarts WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete products from their own shopping carts" ON public.shoppingcart_products
    FOR DELETE USING (
        shoppingcart_id IN (
            SELECT id FROM public.shoppingcarts WHERE user_id = auth.uid()
        )
    );

-- Função para atualizar o timestamp updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para atualizar updated_at automaticamente
CREATE TRIGGER update_shoppingcarts_updated_at 
    BEFORE UPDATE ON public.shoppingcarts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentários nas tabelas
COMMENT ON TABLE public.shoppingcarts IS 'Carrinho de compras dos usuários';
COMMENT ON TABLE public.shoppingcart_products IS 'Produtos no carrinho de compras';
COMMENT ON COLUMN public.shoppingcarts.user_id IS 'ID do usuário dono do carrinho';
COMMENT ON COLUMN public.shoppingcart_products.quantity IS 'Quantidade do produto no carrinho';
COMMENT ON COLUMN public.shoppingcart_products.added_at IS 'Data quando o produto foi adicionado ao carrinho';
