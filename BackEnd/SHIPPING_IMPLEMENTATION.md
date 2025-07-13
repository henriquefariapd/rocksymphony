# Implementação de Frete - Rock Symphony

## Resumo das Alterações

Foi implementada uma funcionalidade completa de cálculo de frete baseada no CEP de origem (24210001) e destino do usuário.

## Arquivos Modificados

### Backend

1. **models.py**
   - Adicionada coluna `shipping_cost` na tabela `Order`
   - Campo `DECIMAL(10,2)` para armazenar o valor do frete

2. **shipping_calculator.py** (NOVO)
   - Classe `ShippingCalculator` para calcular frete por região
   - CEP de origem fixo: 24210001
   - Cálculo baseado nas regiões do Brasil
   - Estimativa de dias de entrega

3. **main.py**
   - Nova rota `/api/calculate-shipping` para calcular frete
   - Modificada função `handle_checkout` para incluir frete
   - Atualizada função `get_user_orders` para retornar shipping_cost
   - Frete incluído nos itens do MercadoPago

### Frontend

4. **App.jsx**
   - Novos estados: `shippingCost`, `isCalculatingShipping`, `shippingDeliveryDays`
   - Função `calculateShipping()` para calcular frete via API
   - Recálculo automático quando endereço muda
   - Interface atualizada com breakdown de valores (produtos + frete)
   - Notificação de sucesso com informações detalhadas

5. **MeusPedidos.jsx**
   - Exibição detalhada do frete nos pedidos
   - Breakdown de valores (produtos + frete)

### Banco de Dados

6. **add_shipping_cost_column.sql** (NOVO)
   - Script SQL para adicionar coluna shipping_cost

7. **add_shipping_column.py** (NOVO)
   - Script Python para migração da coluna

## Como Usar

### 1. Atualizar Banco de Dados

Execute no Supabase SQL Editor:
```sql
ALTER TABLE orders ADD COLUMN IF NOT EXISTS shipping_cost DECIMAL(10,2) DEFAULT 0.00;
COMMENT ON COLUMN orders.shipping_cost IS 'Valor do frete calculado para o pedido';
```

### 2. Funcionamento

1. **Cálculo Automático**: Quando usuário seleciona endereço no carrinho, frete é calculado automaticamente
2. **Exibição**: Valores separados (produtos + frete = total)
3. **Checkout**: Frete incluído no total do pedido e item separado no MercadoPago
4. **Histórico**: Pedidos mostram breakdown de valores

### 3. Valores de Frete por Região

- **Sudeste (SP, RJ, ES, MG)**: R$ 12,00 - R$ 20,00
- **Sul (PR, SC, RS)**: R$ 25,00 - R$ 30,00  
- **Nordeste**: R$ 35,00 - R$ 48,00
- **Norte**: R$ 50,00 - R$ 65,00
- **Centro-Oeste**: R$ 35,00 - R$ 50,00

### 4. Estimativas de Entrega

- **Sudeste**: 3 dias úteis
- **Sul**: 5 dias úteis
- **Nordeste**: 7 dias úteis
- **Norte**: 10-12 dias úteis
- **Centro-Oeste**: 6 dias úteis

## API Endpoints

### POST /api/calculate-shipping
Calcula frete baseado no CEP de destino.

**Request:**
```json
{
  "cep": "01310-100"
}
```

**Response:**
```json
{
  "shipping_cost": 15.00,
  "delivery_days": 3,
  "weight_kg": 0.5,
  "origin_cep": "24210001"
}
```

### POST /api/handle_checkout
Incluído cálculo automático de frete.

**Response atualizada:**
```json
{
  "order_id": 123,
  "total_amount": 65.00,
  "products_total": 50.00,
  "shipping_cost": 15.00,
  "message": "Pedido criado com sucesso"
}
```

## Melhorias Futuras

1. **Integração com Correios**: Substituir tabela de valores por API real dos Correios
2. **Múltiplas Opções**: PAC, SEDEX, etc.
3. **Frete Grátis**: Implementar regras (ex: acima de R$ 100)
4. **Cache**: Armazenar cálculos para evitar recálculos desnecessários
5. **Peso Real**: Calcular peso baseado no produto real ao invés de estimativa

## Configuração de Desenvolvimento

Certifique-se de que o `shipping_calculator.py` está sendo importado corretamente no `main.py` e que a nova coluna foi adicionada ao banco de dados antes de testar.
