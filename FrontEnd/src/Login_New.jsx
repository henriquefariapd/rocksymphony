// Login.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Login.css';

function Login({ setIsLoggedIn }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [isResetMode, setIsResetMode] = useState(false);
  
  // Estados para o cadastro
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerConfirmPassword, setRegisterConfirmPassword] = useState('');
  const [registerUsername, setRegisterUsername] = useState('');
  
  // Estados para recuperação de senha
  const [resetEmail, setResetEmail] = useState('');
  
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token && token != 'undefined') {
      setIsLoggedIn(true);
      navigate('/');
    }
  }, [setIsLoggedIn, navigate]);

  // Função para fazer o login
  const handleLogin = async (e) => {
    e.preventDefault();

    console.log("=== DEBUG LOGIN ===");
    console.log("Email:", email);
    console.log("Password:", password);

    try {
      const apiUrl =
      window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : "https://rock-symphony-91f7e39d835d.herokuapp.com";

      console.log("API URL:", apiUrl);
      console.log("Login URL:", `${apiUrl}/auth/login`);

      console.log("Fazendo requisição...");
      
      try {
        const response = await axios.post(
          `${apiUrl}/auth/login`,
          {
            email: email,
            password: password
          },
          {
            timeout: 10000
          }
        );

        console.log("Requisição completada!");
        console.log("Response status:", response.status);
        console.log("Response data:", response.data);

        if (response.status === 200) {
          console.log("Login successful!");
          localStorage.setItem('access_token', response.data.access_token);
          localStorage.setItem("user_id", response.data.user.id);
          localStorage.setItem("email", response.data.user.email);
          localStorage.setItem("usuario", response.data.user.usuario || '');
          localStorage.setItem("is_admin", response.data.user.is_admin);

          console.log("Data stored in localStorage:");
          console.log("access_token:", response.data.access_token);
          console.log("user_id:", response.data.user.id);
          console.log("email:", response.data.user.email);
          console.log("usuario:", response.data.user.usuario);
          console.log("is_admin:", response.data.user.is_admin);

          setIsLoggedIn(true);
          console.log("Recarregando página...");
          location.reload();
        }
      } catch (requestError) {
        console.error("Erro na requisição:", requestError);
        throw requestError;
      }
    } catch (err) {
      console.error("Erro completo no login:", err);
      console.error("Error message:", err.message);
      console.error("Error response:", err.response?.data);
      console.error("Error status:", err.response?.status);
      console.error("Network error:", err.code);
      
      if (err.code === 'ERR_NETWORK') {
        setError('Erro de conexão. Verifique se o servidor está rodando na porta 8000.');
      } else {
        setError('Erro ao fazer login, tente novamente!');
      }
    }
  };

  // Função para fazer o cadastro
  const handleRegister = async (e) => {
    e.preventDefault();

    console.log("=== DEBUG REGISTER ===");
    console.log("Email:", registerEmail);
    console.log("Username:", registerUsername);

    // Validações
    if (registerPassword !== registerConfirmPassword) {
      setError('As senhas não coincidem.');
      return;
    }

    if (registerPassword.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres.');
      return;
    }

    try {
      const apiUrl =
      window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : "https://rock-symphony-91f7e39d835d.herokuapp.com";

      console.log("API URL:", apiUrl);
      console.log("Register URL:", `${apiUrl}/auth/register`);

      console.log("Fazendo requisição de cadastro...");
      
      const response = await axios.post(
        `${apiUrl}/auth/register`,
        {
          email: registerEmail,
          password: registerPassword,
          usuario: registerUsername
        },
        {
          timeout: 10000
        }
      );

      console.log("Cadastro completado!");
      console.log("Response status:", response.status);
      console.log("Response data:", response.data);

      if (response.status === 200) {
        console.log("Cadastro successful!");
        setSuccess('Cadastro realizado com sucesso! Verifique seu email para confirmar a conta.');
        setError('');
        
        // Limpar campos
        setRegisterEmail('');
        setRegisterPassword('');
        setRegisterConfirmPassword('');
        setRegisterUsername('');
        
        // Voltar para o modo de login após alguns segundos
        setTimeout(() => {
          setIsRegisterMode(false);
          setSuccess('');
        }, 3000);
      }
    } catch (err) {
      console.error("Erro completo no cadastro:", err);
      console.error("Error message:", err.message);
      console.error("Error response:", err.response?.data);
      console.error("Error status:", err.response?.status);
      
      if (err.response?.status === 400) {
        setError('Email já está em uso ou dados inválidos.');
      } else if (err.code === 'ERR_NETWORK') {
        setError('Erro de conexão. Verifique se o servidor está rodando na porta 8000.');
      } else {
        setError('Erro ao fazer cadastro, tente novamente!');
      }
    }
  };

  // Função para alternar entre login e cadastro
  const toggleMode = () => {
    setIsRegisterMode(!isRegisterMode);
    setIsResetMode(false);
    setError('');
    setSuccess('');
    // Limpar campos
    setEmail('');
    setPassword('');
    setRegisterEmail('');
    setRegisterPassword('');
    setRegisterConfirmPassword('');
    setRegisterUsername('');
    setResetEmail('');
  };

  // Função para alternar para o modo de recuperação de senha
  const toggleResetMode = () => {
    setIsResetMode(!isResetMode);
    setIsRegisterMode(false);
    setError('');
    setSuccess('');
    // Limpar campos
    setEmail('');
    setPassword('');
    setRegisterEmail('');
    setRegisterPassword('');
    setRegisterConfirmPassword('');
    setRegisterUsername('');
    setResetEmail('');
  };

  // Função para recuperar senha
  const handlePasswordReset = async (e) => {
    e.preventDefault();

    console.log("=== DEBUG PASSWORD RESET ===");
    console.log("Email:", resetEmail);

    try {
      const apiUrl =
        window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
          ? "http://127.0.0.1:8000"
          : "https://rock-symphony-91f7e39d835d.herokuapp.com";

      console.log("API URL:", apiUrl);
      console.log("Reset URL:", `${apiUrl}/auth/reset-password`);

      console.log("Enviando solicitação de recuperação...");
      
      const response = await axios.post(
        `${apiUrl}/auth/reset-password`,
        {
          email: resetEmail
        },
        {
          timeout: 10000
        }
      );

      console.log("Solicitação completada!");
      console.log("Response status:", response.status);
      console.log("Response data:", response.data);

      if (response.status === 200) {
        console.log("Reset email sent successfully!");
        setSuccess('Email de recuperação enviado! Verifique sua caixa de entrada.');
        setError('');
        
        // Limpar campo
        setResetEmail('');
        
        // Voltar para o modo de login após alguns segundos
        setTimeout(() => {
          setIsResetMode(false);
          setSuccess('');
        }, 5000);
      }
    } catch (err) {
      console.error("Erro na recuperação de senha:", err);
      console.error("Error message:", err.message);
      console.error("Error response:", err.response?.data);
      console.error("Error status:", err.response?.status);
      
      if (err.response?.status === 400) {
        setError('Email não encontrado ou inválido.');
      } else if (err.code === 'ERR_NETWORK') {
        setError('Erro de conexão. Verifique se o servidor está rodando.');
      } else {
        setError('Erro ao enviar email de recuperação, tente novamente!');
      }
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <h2>Rock Symphony</h2>
        
        {isResetMode ? (
          // Formulário de recuperação de senha
          <form onSubmit={handlePasswordReset}>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={resetEmail}
                onChange={(e) => setResetEmail(e.target.value)}
                placeholder="Digite seu email para recuperar a senha"
                required
              />
            </div>
            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
            <button type="submit">Enviar Email de Recuperação</button>
          </form>
        ) : (
          // Formulário de login/cadastro
          <form onSubmit={isRegisterMode ? handleRegister : handleLogin}>
            {isRegisterMode && (
              <div className="form-group">
                <label>Nome de Usuário</label>
                <input
                  type="text"
                  value={registerUsername}
                  onChange={(e) => setRegisterUsername(e.target.value)}
                  placeholder="Digite seu nome de usuário"
                  required
                />
              </div>
            )}
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={isRegisterMode ? registerEmail : email}
                onChange={(e) => isRegisterMode ? setRegisterEmail(e.target.value) : setEmail(e.target.value)}
                placeholder="admin@rocksymphony.com"
                required
              />
            </div>
            <div className="form-group">
              <label>Senha</label>
              <input
                type="password"
                value={isRegisterMode ? registerPassword : password}
                onChange={(e) => isRegisterMode ? setRegisterPassword(e.target.value) : setPassword(e.target.value)}
                placeholder="Digite sua senha"
                required
              />
            </div>
            {isRegisterMode && (
              <div className="form-group">
                <label>Confirmar Senha</label>
                <input
                  type="password"
                  value={registerConfirmPassword}
                  onChange={(e) => setRegisterConfirmPassword(e.target.value)}
                  placeholder="Confirme sua senha"
                  required
                />
              </div>
            )}
            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
            <button type="submit">{isRegisterMode ? 'Cadastrar' : 'Entrar'}</button>
          </form>
        )}
        
        <div className="toggle-mode">
          {isResetMode ? (
            <p>
              Lembrou da senha? <span onClick={toggleResetMode}>Voltar ao login</span>
            </p>
          ) : isRegisterMode ? (
            <>
              <p>
                Já tem uma conta? <span onClick={toggleMode}>Entre aqui</span>
              </p>
            </>
          ) : (
            <>
              <p>
                Não tem uma conta? <span onClick={toggleMode}>Cadastre-se</span>
              </p>
              <p>
                Esqueceu a senha? <span onClick={toggleResetMode}>Recuperar senha</span>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Login;
