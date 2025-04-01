import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Home from './Home';
import axios from 'axios';
import Header from './Header';
import Espacos from './Espacos'; // Página para listar espaços
import MinhasReservas from './MinhasReservas'; // Página para cadastrar espaços
import Reservas from './Reservas';
import Configuracoes from './Configuracoes';
import ImportarUsuarios from './ImportarUsuarios';
import ListaUsuarios from './Usuarios';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  // Definir a URL base da API
  const apiUrl =
    window.location.hostname === "localhost"
      ? "http://localhost:8000"
      : "https://ta-reservado-8e74d7e79187.herokuapp.com";

  // Função para buscar as informações do usuário e verificar se é admin
  const fetchMe = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if ((!token || token == 'undefined')) return;  
      const response = await axios.post(
        `${apiUrl}/me`,
        {}, // Agora não passamos username no corpo
        {
          headers: {
            Authorization: `Bearer ${token}`, // Passamos o token no cabeçalho
          },
        }
      );
  
      setIsAdmin(response.data.is_admin);
    } catch (err) {
      localStorage.removeItem("access_token");
      console.error("Erro ao recuperar usuário:", err);
    }
  };

  // Verificar o token no localStorage ao iniciar a aplicação
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token && token != 'undefined') {
      setIsLoggedIn(true);
      fetchMe(); // Após o login, chama fetchMe para definir isAdmin
    }
  }, []);

  // Função para fazer logout
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    setIsLoggedIn(false);
    setIsAdmin(false); // Garantir que isAdmin também seja resetado
    window.location.href = '/';
  };

  return (
    <Router>
      <Header isLoggedIn={isLoggedIn} isAdmin={isAdmin} onLogout={handleLogout} />
      <Routes>
        <Route path="/" element={isLoggedIn ? <Home /> : <Navigate to="/login" />} />
        <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
        
        {/* Protegendo as rotas de espaços e reservas */}
        {isLoggedIn ? (
          <>
            <Route path="/espacos" element={<Espacos />} />
            <Route path="/minhas-reservas" element={<MinhasReservas />} />
            <Route path="/reservas" element={<Reservas isAdmin={isAdmin} />} />
            <Route path="/configuracoes" element={<Configuracoes/>} />
            <Route path="/importar-usuarios" element={<ImportarUsuarios/>} />
            <Route path="/usuarios" element={<ListaUsuarios/>} />
          </>
        ) : (
          <>
            <Route path="/login" element={<Navigate to="/login" />} />
            <Route path="/cadastro-espaco" element={<Navigate to="/login" />} />
          </>
        )}
      </Routes>
    </Router>
  );
}

export default App;
