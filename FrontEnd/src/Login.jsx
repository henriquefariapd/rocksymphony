// Login.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Login.css';

function Login({ setIsLoggedIn }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token && token != 'undefined') {
      setIsLoggedIn(true);  // Atualiza o estado de login diretamente ao carregar
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
            timeout: 10000 // 10 segundos de timeout
          }
        );

        console.log("Requisição completada!");
        console.log("Response status:", response.status);
        console.log("Response data:", response.data);

        if (response.status === 200) {
          console.log("Login successful!");
          // Armazenar o token no localStorage
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

          // Atualizar o estado de login
          setIsLoggedIn(true);  // Alterar para refletir que o usuário está logado
          console.log("Recarregando página...");
          location.reload();
            // Redireciona para a página principal
        }
      } catch (requestError) {
        console.error("Erro na requisição:", requestError);
        throw requestError; // Re-throw para ser capturado pelo catch externo
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

  return (
    <div className="login-page">
      <div className="login-container">
        <h2>Rock Symphony</h2>
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@rocksymphony.com"
              required
            />
          </div>
          <div className="form-group">
            <label>Senha</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Digite sua senha"
              required
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit">Entrar</button>
        </form>
      </div>
    </div>
  );
}

export default Login;
