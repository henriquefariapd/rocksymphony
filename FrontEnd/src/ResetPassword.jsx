// ResetPassword.jsx
import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import './ResetPassword.css';

function ResetPassword() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [accessToken, setAccessToken] = useState('');
  const [refreshToken, setRefreshToken] = useState('');
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // Obter os parâmetros da URL (access_token, refresh_token, error, etc.)
  const errorParam = searchParams.get('error');
  const errorDescription = searchParams.get('error_description');
  const errorCode = searchParams.get('error_code');

  useEffect(() => {
    // Os tokens do Supabase vêm como fragmentos (após #) na URL
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    
    const accessToken = params.get('access_token');
    const refreshToken = params.get('refresh_token');
    const tokenType = params.get('token_type');
    const expiresAt = params.get('expires_at');
    const type = params.get('type');
    
    console.log('=== DEBUG RESET PASSWORD TOKENS ===');
    console.log('Hash:', hash);
    console.log('Access Token:', accessToken);
    console.log('Refresh Token:', refreshToken);
    console.log('Token Type:', tokenType);
    console.log('Expires At:', expiresAt);
    console.log('Type:', type);
    
    if (accessToken && type === 'recovery') {
      // Tokens válidos encontrados
      console.log('Tokens válidos encontrados');
      setAccessToken(accessToken);
      setRefreshToken(refreshToken);
    } else {
      console.log('Tokens não encontrados ou inválidos');
      setError('Link de recuperação inválido. Por favor, solicite um novo link.');
    }
  }, []);

  const verifyToken = async () => {
    // Função removida - não é mais necessária pois validamos diretamente na URL
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validações
    if (password !== confirmPassword) {
      setError('As senhas não coincidem.');
      return;
    }

    if (password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres.');
      return;
    }

    if (!accessToken) {
      setError('Link de recuperação inválido ou expirado.');
      return;
    }

    setLoading(true);

    try {
      const apiUrl =
        window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
          ? "http://127.0.0.1:8000"
          : "https://rock-symphony-91f7e39d835d.herokuapp.com";

      console.log("=== DEBUG RESET PASSWORD ===");
      console.log("Access Token:", accessToken);
      console.log("New Password:", password);

      const response = await axios.post(
        `${apiUrl}/auth/update-password`,
        {
          password: password,
          access_token: accessToken,
          refresh_token: refreshToken
        },
        {
          timeout: 10000
        }
      );

      if (response.status === 200) {
        setSuccess('Senha redefinida com sucesso! Você será redirecionado para o login.');
        setPassword('');
        setConfirmPassword('');
        
        // Redirecionar para login após 3 segundos
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      }
    } catch (err) {
      console.error("Erro ao redefinir senha:", err);
      
      if (err.response?.status === 400) {
        setError('Link de recuperação inválido ou expirado.');
      } else if (err.response?.status === 422) {
        setError('Senha inválida. Tente novamente.');
      } else if (err.code === 'ERR_NETWORK') {
        setError('Erro de conexão. Tente novamente mais tarde.');
      } else {
        setError('Erro ao redefinir senha. Tente novamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reset-password-page">
      <div className="reset-password-container">
        <div className="reset-password-header">
          <h1>Rock Symphony</h1>
          <h2>Redefinir Senha</h2>
        </div>

        {!accessToken ? (
          <div className="error-state">
            <p>{error || 'Link de recuperação inválido ou expirado.'}</p>
            <div className="error-actions">
              <button 
                onClick={() => navigate('/login')}
                className="btn-back-to-login"
              >
                Voltar ao Login
              </button>
              <button 
                onClick={() => navigate('/login')}
                className="btn-request-new-link"
              >
                Solicitar Novo Link
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="reset-password-form">
            <div className="form-group">
              <label htmlFor="password">Nova Senha</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Digite sua nova senha"
                required
                minLength={6}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirmar Nova Senha</label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirme sua nova senha"
                required
                minLength={6}
                disabled={loading}
              />
            </div>

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}

            <button 
              type="submit" 
              disabled={loading}
              className="btn-reset-password"
            >
              {loading ? 'Redefinindo...' : 'Redefinir Senha'}
            </button>
          </form>
        )}

        <div className="reset-password-footer">
          <p>
            Lembrou da senha? <span onClick={() => navigate('/login')}>Voltar ao Login</span>
          </p>
        </div>
      </div>
    </div>
  );
}

export default ResetPassword;
