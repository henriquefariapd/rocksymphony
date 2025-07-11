# Rock Symphony - Marketplace de CDs de Rock

Sistema de marketplace para CDs de rock com FastAPI (Backend) e React + Vite (Frontend), integrado com Supabase.

## 📋 Pré-requisitos

- Python 3.9+
- Node.js (versão 16+ recomendada)
- npm ou yarn
- Conta no Supabase

## 🔧 Configuração do Supabase

### 1. No seu projeto Supabase:
1. Acesse o [Supabase Dashboard](https://app.supabase.com/)
2. Vá em **Settings** > **Database**
3. Copie a **Connection String** (formato: `postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres`)
4. Vá em **Settings** > **API** e copie:
   - **URL**: `https://[YOUR-PROJECT-REF].supabase.co`
   - **anon key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### 2. Configure o arquivo .env:
No arquivo `BackEnd/.env`, substitua os valores:
```env
SUPABASE_URL=https://YOUR-PROJECT-REF.supabase.co
SUPABASE_KEY=YOUR-ANON-KEY
DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@YOUR-PROJECT-REF.supabase.co:5432/postgres
```

## 🚀 Como executar o projeto

### 1. Configuração inicial

Clone o repositório:
```bash
git clone <url-do-repositorio>
cd rocksymphony
```

### 2. Backend (FastAPI)

#### Instalar dependências:
```bash
cd BackEnd
pip install -r requirements.txt
```

#### Executar o servidor:
```bash
uvicorn main:app --reload
```

O backend estará disponível em:
- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc

### 3. Frontend (React + Vite)

#### Instalar dependências:
```bash
cd FrontEnd
npm install
```

#### Executar o servidor de desenvolvimento:
```bash
npm run dev
```

O frontend estará disponível em: http://localhost:5173

### 4. Executar ambos simultaneamente

1. **Terminal 1 (Backend)**:
   ```bash
   cd BackEnd
   uvicorn main:app --reload
   ```

2. **Terminal 2 (Frontend)**:
   ```bash
   cd FrontEnd
   npm run dev
   ```

## 📁 Estrutura do projeto

```
rocksymphony/
├── BackEnd/           # API FastAPI
│   ├── main.py        # Arquivo principal da API
│   ├── models.py      # Modelos do banco de dados
│   ├── schemas.py     # Schemas Pydantic
│   ├── auth.py        # Autenticação
│   ├── supabase_client.py # Cliente Supabase
│   ├── config.py      # Configurações
│   ├── .env          # Variáveis de ambiente
│   └── requirements.txt
├── FrontEnd/          # App React
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🗃️ Modelos do Banco de Dados

### Tabelas principais:
- **users**: Usuários do sistema
- **products**: CDs de rock (álbuns)
- **orders**: Pedidos realizados
- **shoppingcarts**: Carrinhos de compras
- **order_products**: Produtos por pedido
- **shoppingcart_products**: Produtos no carrinho

### Campos dos produtos (CDs):
- Nome do álbum
- Artista/Banda
- Descrição
- Preço
- Estoque disponível
- Imagem
- Gênero musical
- Ano de lançamento
- Gravadora

## 🛠️ Scripts disponíveis

### Backend
- `uvicorn main:app --reload` - Inicia o servidor com hot reload
- `uvicorn main:app` - Inicia o servidor em produção

### Frontend
- `npm run dev` - Inicia o servidor de desenvolvimento
- `npm run build` - Cria build de produção
- `npm run preview` - Visualiza o build de produção
- `npm run lint` - Executa o linter

## 🔧 Tecnologias utilizadas

### Backend
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
- Supabase (PostgreSQL)
- Bcrypt (para hash de senhas)
- Python-dotenv

### Frontend
- React
- Vite
- JavaScript/JSX
- CSS

## 📝 Notas importantes

- O backend roda na porta 8000 por padrão
- O frontend roda na porta 5173 por padrão (Vite)
- Certifique-se de configurar corretamente as variáveis de ambiente no Supabase
- As tabelas serão criadas automaticamente no primeiro run
- Para desenvolvimento local, certifique-se de que o .env está configurado corretamente