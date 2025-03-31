// Login.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Login.css';

function Login({ setIsLoggedIn }) {
  const [username, setUsername] = useState('');
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

    try {
      const apiUrl =
      window.location.hostname === "localhost"
        ? "http://localhost:8000"
        : "https://ta-reservado-8e74d7e79187.herokuapp.com";

      const response = await axios.post(
        `${apiUrl}/login`,
        {
          username: username,
          password: password
        }
      );

      if (response.status === 200) {
        // Armazenar o token no localStorage
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem("username", response.data.username);
        localStorage.setItem("is_admin", response.data.is_admin);
        localStorage.setItem("userId", response.data.user_id);

        // Atualizar o estado de login
        setIsLoggedIn(true);  // Alterar para refletir que o usuário está logado
        location.reload();
          // Redireciona para a página principal
      }
    } catch (err) {
      console.error("Erro no login:", err);
      setError('Erro ao fazer login, tente novamente!');
    }
  };

  return (
    <div className="login-container">
      <div>
        <h2>Login</h2>
      </div>
      <form onSubmit={handleLogin}>
        <div className="inner-container">
          <label className="align-center">Usuário</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="inner-container">
          <label className="align-center">Senha</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <p className="error">{error}</p>}
        <button type="submit">Entrar</button>
      </form>
    </div>
  );
}

export default Login;
