# Guia de Teste - Recuperação de Senha

## Como testar a funcionalidade de recuperação de senha:

### 1. Configuração do Supabase
No painel do Supabase:
- Vá para Authentication > Settings
- Em "Site URL", adicione: `http://localhost:5173`
- Em "Redirect URLs", adicione: `http://localhost:5173/reset-password`

### 2. Teste no Frontend

1. **Acesse a página de login**: `http://localhost:5173/login`
2. **Clique em "Esqueceu a senha?"**
3. **Digite um email válido cadastrado no sistema**
4. **Clique em "Enviar Email de Recuperação"**
5. **Verifique o email** (pode estar na pasta de spam)
6. **Clique no link do email** - deve redirecionar para `/reset-password`
7. **Digite a nova senha** e confirme
8. **Clique em "Redefinir Senha"**

### 3. Possíveis problemas e soluções:

#### Problema: "OTP Expired" ou "Access Denied"
**Solução**: 
- Verifique se as URLs estão configuradas corretamente no Supabase
- O token do email tem um tempo de expiração limitado
- Solicite um novo link se o erro persistir

#### Problema: Link não funciona
**Solução**:
- Verifique se o backend está rodando na porta 8000
- Verifique se o frontend está rodando na porta 5173
- Confirme as configurações do Supabase

### 4. URLs importantes:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Página de reset: `http://localhost:5173/reset-password`
- API de reset: `http://localhost:8000/auth/reset-password`

### 5. Logs para debug:
- Console do browser (F12)
- Console do backend
- Verifique os parâmetros da URL no reset-password

### 6. Estrutura do fluxo:
1. Usuário solicita reset → Backend envia email via Supabase
2. Usuário clica no link do email → Supabase redireciona para nossa página
3. Nossa página verifica os tokens → Se válidos, permite mudança de senha
4. Usuário define nova senha → Backend atualiza via Supabase
5. Sucesso → Redireciona para login
