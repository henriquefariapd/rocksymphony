import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Home from './Home';
import axios from 'axios';
import Header from './Header';
import Espacos from './Espacos';
import MinhasReservas from './MinhasReservas';
import Reservas from './Reservas';
import Configuracoes from './Configuracoes';
import ImportarUsuarios from './ImportarUsuarios';
import ListaUsuarios from './Usuarios';
import { CiShoppingCart } from "react-icons/ci";
import { IoIosCloseCircleOutline } from "react-icons/io";



function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [sidebarAberto, setSidebarAberto] = useState(false);

  const toggleSidebar = () => {
    setSidebarAberto(!sidebarAberto);
  };

  const apiUrl =
    window.location.hostname === "localhost"
      ? "http://localhost:8000"
      : "https://rock-symphony-91f7e39d835d.herokuapp.com";

  const fetchMe = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token || token === 'undefined') return;
      const response = await axios.post(
        `${apiUrl}/me`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setIsAdmin(response.data.is_admin);
    } catch (err) {
      localStorage.removeItem("access_token");
      console.error("Erro ao recuperar usuário:", err);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token && token !== 'undefined') {
      setIsLoggedIn(true);
      fetchMe();
    }
  }, []);

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
      
      {/* <button
        onClick={toggleSidebar}
        className={`abrir-sidebar ${sidebarAberto ? 'sidebar-aberta' : ''}`}
      >
        <CiShoppingCart />
      </button> */}

      <div className={`sidebar ${sidebarAberto ? 'aberto' : ''}`}>
        <button onClick={toggleSidebar} className="fechar-sidebar"><IoIosCloseCircleOutline/></button>
        <h2 className='sidebar-title'>Seu Carrinho</h2>
        <p>Seu carrinho está vazio.</p>
        <button
          onClick={toggleSidebar}
          className={`abrir-sidebar ${sidebarAberto ? 'sidebar-aberta' : ''}`}
        >
          <CiShoppingCart />
        </button>
      </div>

      <Routes>
        <Route path="/" element={isLoggedIn ? <Home /> : <Navigate to="/login" />} />
        <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
        <Route path="/espacos" element={<Espacos />} />
        <Route path="/minhas-reservas" element={<MinhasReservas />} />
        <Route path="/reservas" element={<Reservas />} />
        <Route path="/configuracoes" element={<Configuracoes />} />
        <Route path="/importar-usuarios" element={<ImportarUsuarios />} />
        <Route path="/usuarios" element={<ListaUsuarios />} />
      </Routes>
    </Router>
  );
}

export default App;
