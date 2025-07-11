import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Login from './Login';
import Home from './Home';
import ResetPassword from './ResetPassword';
import axios from 'axios';
import Header from './Header';
import Produtos from './Produtos';
import MinhasReservas from './MinhasReservas';
import Reservas from './Reservas';
import Configuracoes from './Configuracoes';
import ImportarUsuarios from './ImportarUsuarios';
import ListaUsuarios from './Usuarios';
import LoginModal from './LoginModal';
import { CiShoppingCart } from "react-icons/ci";
import { IoIosCloseCircleOutline } from "react-icons/io";
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [sidebarAberto, setSidebarAberto] = useState(false);
  const [cartItems, setCartItems] = useState([]); // Estado para armazenar os itens do carrinho
  const [showLoginModal, setShowLoginModal] = useState(false);

  const toggleSidebar = () => {
    setSidebarAberto(!sidebarAberto);
  };

  const handleLogin = () => {
    setShowLoginModal(true);
  };

  const apiUrl =
    window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
      ? "http://127.0.0.1:8000"
      : "https://rock-symphony-91f7e39d835d.herokuapp.com";

  // Função para buscar os dados do usuário (usuário logado)
  const fetchMe = async () => {
    try {
      const token = localStorage.getItem("access_token");
      console.log("=== DEBUG FETCH ME ===");
      console.log("Token:", token);
      console.log("URL:", `${apiUrl}/api/me`);
      
      if (!token || token === 'undefined') return;
      const response = await axios.get(
        `${apiUrl}/api/me`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log("FetchMe response:", response.data);
      setIsAdmin(response.data.is_admin);
    } catch (err) {
      console.error("Erro ao recuperar usuário:", err);
      console.error("Error response:", err.response?.data);
      localStorage.removeItem("access_token");
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

  // Função para remover produto do carrinho
  const handleRemoveFromCart = async (productId) => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token || token === 'undefined') {
        console.error("Token não encontrado");
        return;
      }

      console.log(`Removendo produto ${productId} do carrinho...`);
      
      const response = await fetch(`${apiUrl}/api/remove_product_from_cart`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ 
          productId: productId
        }),
      });

      const data = await response.json();
      console.log("Resposta do backend:", data);

      if (!response.ok) {
        throw new Error(data.detail || "Falha ao remover produto do carrinho");
      }

      // Atualizar lista do carrinho
      fetchCartItems();
      
      console.log("Produto removido com sucesso:", data.message);
    } catch (error) {
      console.error("Erro ao remover produto:", error);
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

  // Função para lidar com o login bem-sucedido
  const handleLoginSuccess = () => {
    setShowLoginModal(false);
    const token = localStorage.getItem("access_token");
    if (token && token !== 'undefined') {
      setIsLoggedIn(true);
      fetchMe();
      fetchCartItems();
    }
  };

  return (
    <Router>
      <Header isLoggedIn={isLoggedIn} isAdmin={isAdmin} onLogout={handleLogout} onLogin={handleLogin} />

      {/* Modal de Login */}
      <LoginModal 
        isOpen={showLoginModal} 
        onClose={() => setShowLoginModal(false)}
        onLoginSuccess={handleLoginSuccess}
      />

      {isLoggedIn && (
        <>
          {/* Botão flutuante para abrir o carrinho */}
          <button
            onClick={toggleSidebar}
            className={`btn-carrinho-flutuante ${sidebarAberto ? 'hidden' : ''}`}
          >
            <CiShoppingCart />
            {cartItems.length > 0 && (
              <span className="badge-carrinho">{cartItems.length}</span>
            )}
          </button>

          {/* Overlay para fechar sidebar ao clicar fora */}
          {sidebarAberto && (
            <div 
              className="sidebar-overlay" 
              onClick={toggleSidebar}
            ></div>
          )}

          {/* Sidebar do carrinho */}
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
                        <div className="cart-item-info">
                          <span className="item-name">{item.name}</span>
                          <span className="item-artist">{item.artist}</span>
                        </div>
                        <div className="cart-item-controls">
                          <div className="quantity-info">
                            <span>{item.quantity} x R$ {item.valor}</span>
                          </div>
                          <button 
                            onClick={() => handleRemoveFromCart(item.id)}
                            className="btn-remove-item"
                            title="Remover uma unidade"
                          >
                            -
                          </button>
                        </div>
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
          </div>
        </>
      )}


      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
        <Route path="/produtos" element={<Produtos />} />
        <Route path="/minhas-reservas" element={isLoggedIn ? <MinhasReservas /> : <Navigate to="/login" />} />
        <Route path="/pedidos" element={isLoggedIn ? <Reservas /> : <Navigate to="/login" />} />
        <Route path="/configuracoes" element={isLoggedIn ? <Configuracoes /> : <Navigate to="/login" />} />
        <Route path="/importar-usuarios" element={isLoggedIn ? <ImportarUsuarios /> : <Navigate to="/login" />} />
        <Route path="/usuarios" element={isLoggedIn ? <ListaUsuarios /> : <Navigate to="/login" />} />
        <Route path="/reset-password" element={<ResetPassword />} />
      </Routes>
    </Router>
  );
}

export default App;
