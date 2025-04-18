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
  const [cartItems, setCartItems] = useState([]); // Estado para armazenar os itens do carrinho

  const toggleSidebar = () => {
    setSidebarAberto(!sidebarAberto);
  };

  const apiUrl =
    window.location.hostname === "localhost"
      ? "http://localhost:8000"
      : "https://rock-symphony-91f7e39d835d.herokuapp.com";

  // Função para buscar os dados do usuário (usuário logado)
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

  // Função para buscar os produtos do carrinho
  const fetchCartItems = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token || token === 'undefined') return;
      
      const response = await axios.get(`${apiUrl}/api/get_cart_products`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setCartItems(response.data); // Armazenar os produtos no estado
    } catch (err) {
      console.error("Erro ao recuperar produtos do carrinho:", err);
    }
  };
  const handleCheckout = async (productId) => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token || token == 'undefined') {
        toast.error("Usuário não autenticado. Por favor, faça login.");
        return;
      }

      const response = await fetch(`${apiUrl}/api/handle_checkout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ 
          productId
        }),
      });
  
      const data = await response.json();
      window.location.reload();
      console.log("Resposta do backend:", data);
  
      if (!response.ok) {
        throw new Error(data.detail || "Falha ao reservar o espaço");
      }
  
      // setIsModalOpen(false);
      fetchSchedulesAndSpaces();
  
      toast(`${spaceName} foi reservado com sucesso!`, {
        position: "top-right",
        autoClose: 3000,
      });
    } catch (error) {
      console.error("Erro ao reservar:", error);
      toast.error("Erro ao reservar o espaço. Tente novamente.", {
        position: "top-right",
        autoClose: 3000,
      });
    }
  }; 

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token && token !== 'undefined') {
      setIsLoggedIn(true);
      fetchMe();
      fetchCartItems(); // Buscar os produtos do carrinho
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

      {isLoggedIn && (
        <div className={`sidebar ${sidebarAberto ? 'aberto' : ''}`}>
          <button onClick={toggleSidebar} className="fechar-sidebar">
            <IoIosCloseCircleOutline />
          </button>
          <h2 className="sidebar-title">Seu Carrinho</h2>
          {cartItems.length > 0 ? (
            <>
              <ul>
                {cartItems.map((item) => (
                  <li key={item.id} className="cart-item">
                    <div className="cart-item-details">
                      <span>{item.name}</span>
                      <span>{item.quantity} x {item.valor} R$</span> {/* Exibe a quantidade e o valor */}
                    </div>
                  </li>
                ))}
              </ul>
              <div className="cart-summary">
                <p>
                  <strong>Total:</strong> R$ {cartItems.reduce((total, item) => total + item.valor * item.quantity, 0).toFixed(2)}
                </p>
              </div>
              <div>
                <button
                  className="btn-continuar-pagamento"
                  onClick={() => handleCheckout()}
                >
                  Efetuar Pedido
                </button>
              </div>
            </>
          ) : (
            <p>Seu carrinho está vazio.</p>
          )}
          <button
            onClick={toggleSidebar}
            className={`abrir-sidebar ${sidebarAberto ? 'sidebar-aberta' : ''}`}
          >
            <CiShoppingCart />
          </button>
        </div>
      )}


      <Routes>
        <Route path="/" element={isLoggedIn ? <Home /> : <Navigate to="/login" />} />
        <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
        <Route path="/espacos" element={<Espacos />} />
        <Route path="/minhas-reservas" element={<MinhasReservas />} />
        <Route path="/pedidos" element={<Reservas />} />
        <Route path="/configuracoes" element={<Configuracoes />} />
        <Route path="/importar-usuarios" element={<ImportarUsuarios />} />
        <Route path="/usuarios" element={<ListaUsuarios />} />
      </Routes>
    </Router>
  );
}

export default App;
