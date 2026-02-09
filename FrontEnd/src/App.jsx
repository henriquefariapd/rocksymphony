import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, Link, useLocation } from 'react-router-dom';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import toast2, { Toaster } from 'react-hot-toast';
import Login from './Login';
import Home from './Home';
import ResetPassword from './ResetPassword';
import axios from 'axios';
import Header from './Header';
import Footer from './Footer';
import Produtos from './Produtos';
import MeusPedidos from './MeusPedidos';
import Pedidos from './Pedidos';
import AdminPedidos from './AdminPedidos';
import Configuracoes from './Configuracoes';
import ImportarUsuarios from './ImportarUsuarios';
import UsuariosNovaTabela from './UsuariosNovaTabela';
import Conta from './Conta';
import MapaDoRock from './MapaDoRock';
import Artistas from './Artistas';
import LoginModal from './LoginModal';
import { CiShoppingCart } from "react-icons/ci";
import { IoIosCloseCircleOutline } from "react-icons/io";
import { FaMapMarkerAlt } from "react-icons/fa";
import './App.css';
import Camisas from './Camisas';
import VerCamisas from './VerCamisas';

function App() {
  return (
    <>
      <Router>
        <AppContent />
      </Router>
    </>
  );
}

function AppContent() {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [sidebarAberto, setSidebarAberto] = useState(false);
  const [cartItems, setCartItems] = useState([]); // Estado para armazenar os itens do carrinho
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [userAddresses, setUserAddresses] = useState([]); // Endereços do usuário
  const [selectedAddressId, setSelectedAddressId] = useState(null); // Endereço selecionado
  const [shippingCost, setShippingCost] = useState(0); // Valor do frete
  const [isCalculatingShipping, setIsCalculatingShipping] = useState(false); // Loading do cálculo de frete
  const [shippingDeliveryDays, setShippingDeliveryDays] = useState(0); // Dias de entrega

  // Hook para efeito parallax
  useEffect(() => {
    const handleScroll = () => {
      const scrolled = window.pageYOffset;
      const rate = scrolled * 0.3; // Velocidade do parallax
      
      // Aplica o parallax criando um novo estilo CSS
      let style = document.getElementById('dynamic-parallax');
      if (!style) {
        style = document.createElement('style');
        style.id = 'dynamic-parallax';
        document.head.appendChild(style);
      }
      
      style.textContent = `
        .app-container::before {
          transform: translateY(${rate}px) !important;
        }
      `;
      
      console.log('Parallax aplicado - Scroll:', scrolled, 'Transform:', rate);
    };

    // Throttle simples
    let ticking = false;
    const requestTick = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          handleScroll();
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', requestTick, { passive: true });
    handleScroll(); // Executa uma vez

    return () => {
      window.removeEventListener('scroll', requestTick);
      const style = document.getElementById('dynamic-parallax');
      if (style) {
        style.remove();
      }
    };
  }, []);

  const toggleSidebar = () => {
    const wasOpen = sidebarAberto;
    setSidebarAberto(!sidebarAberto);
    
    // Se o carrinho está sendo aberto (não estava aberto antes), calcular frete automaticamente
    if (!wasOpen && selectedAddressId && cartItems.length > 0) {
      calculateShipping(selectedAddressId);
    }
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
      debugger
      setCartItems(response.data); // Armazenar os produtos no estado
      
      // Se já houver um endereço selecionado, calcular frete automaticamente
      if (selectedAddressId && response.data.length > 0) {
        calculateShipping(selectedAddressId);
      }
    } catch (err) {
      console.error("Erro ao recuperar produtos do carrinho:", err);
    }
  };

  // Função para calcular o frete
  const calculateShipping = async (addressId) => {
    try {
      if (!addressId) {
        setShippingCost(0);
        setShippingDeliveryDays(0);
        return;
      }

      const token = localStorage.getItem("access_token");
      if (!token || token === 'undefined') return;

      setIsCalculatingShipping(true);

      // Buscar dados do endereço
      const address = userAddresses.find(addr => addr.id === addressId);
      if (!address) return;

      const response = await axios.post(`${apiUrl}/api/calculate-shipping`, {
        cep: address.cep
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setShippingCost(response.data.shipping_cost);
      setShippingDeliveryDays(response.data.delivery_days);
    } catch (err) {
      console.error("Erro ao calcular frete:", err);
      toast.error("Erro ao calcular frete. Valor padrão será aplicado.");
      setShippingCost(35.00); // Valor padrão
      setShippingDeliveryDays(7);
    } finally {
      setIsCalculatingShipping(false);
    }
  };

  const handleCheckout = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token || token == 'undefined') {
        toast.error("Usuário não autenticado. Por favor, faça login.");
        return;
      }

      if (!selectedAddressId) {
        toast.error("Por favor, selecione um endereço de entrega.");
        return;
      }

      const response = await fetch(`${apiUrl}/api/handle_checkout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          address_id: selectedAddressId
        })
      });
  
      const data = await response.json();
      console.log("Resposta do backend:", data);
  
      if (!response.ok) {
        throw new Error(data.detail || "Falha ao criar pedido");
      }
  
      // Atualizar carrinho após criar pedido
      fetchCartItems();
      
      // Fechar sidebar
      setSidebarAberto(false);
      
      // Notificação especial de pedido criado com react-hot-toast
      toast2.success(
        (t) => (
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '20px', marginBottom: '8px' }}>🎉</div>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
              Pedido #{data.order_id} criado!
            </div>
            <div style={{ fontSize: '14px', color: '#666' }}>
              Total: R$ {data.total_amount?.toFixed(2)}
            </div>
            {data.shipping_cost && (
              <div style={{ fontSize: '12px', color: '#888' }}>
                (Produtos: R$ {data.products_total?.toFixed(2)} + Frete: R$ {data.shipping_cost?.toFixed(2)})
              </div>
            )}
            <div style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
              Redirecionando para seus pedidos...
            </div>
          </div>
        ),
        {
          duration: 2000,
          position: 'top-center',
          style: {
            background: '#10B981',
            color: 'white',
            padding: '16px',
            borderRadius: '12px',
            boxShadow: '0 10px 40px rgba(16, 185, 129, 0.3)',
          },
        }
      );

      // Redirecionar para Meus Pedidos após 1.5 segundos
      setTimeout(() => {
        navigate('/minhas-reservas');
      }, 1500);
    } catch (error) {
      console.error("Erro ao criar pedido:", error);
      toast.error("Erro ao criar pedido. Tente novamente.", {
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

  // Função para buscar os endereços do usuário
  const fetchUserAddresses = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token || token === 'undefined') return;
      
      const response = await axios.get(`${apiUrl}/api/addresses`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setUserAddresses(response.data);
      
      // Selecionar automaticamente o endereço padrão se existir
      const defaultAddress = response.data.find(addr => addr.is_default);
      if (defaultAddress) {
        setSelectedAddressId(defaultAddress.id);
        calculateShipping(defaultAddress.id); // Calcular frete automaticamente
      }
    } catch (err) {
      console.error("Erro ao recuperar endereços:", err);
    }
  };

  // Função para recarregar endereços (para ser chamada após cadastrar novo endereço)
  const refreshAddresses = () => {
    fetchUserAddresses();
  };

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token && token !== 'undefined') {
      setIsLoggedIn(true);
      fetchMe();
      fetchCartItems(); // Buscar os produtos do carrinho
      fetchUserAddresses(); // Buscar endereços do usuário
      fetchUserAddresses(); // Buscar endereços do usuário
    }
  }, []);

  // Calcular frete automaticamente quando endereço ou itens do carrinho mudarem
  useEffect(() => {
    if (selectedAddressId && cartItems.length > 0 && sidebarAberto) {
      calculateShipping(selectedAddressId);
    } else if (!selectedAddressId || cartItems.length === 0) {
      // Resetar frete se não houver endereço ou itens
      setShippingCost(0);
      setShippingDeliveryDays(0);
    }
  }, [selectedAddressId, cartItems.length, sidebarAberto]);

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
      fetchUserAddresses();
    }
  };

  return (
    <div className="app-container">
      <Toaster />
      <ToastContainer 
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
      <Header isLoggedIn={isLoggedIn} isAdmin={isAdmin} onLogout={handleLogout} onLogin={handleLogin} />

      {/* Modal de Login */}
      <LoginModal 
        isOpen={showLoginModal} 
        onClose={() => setShowLoginModal(false)}
        onLoginSuccess={handleLoginSuccess}
      />

      <main className="main-content">

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
                {/* Seletor de Endereço */}
                <div className="address-selection">
                  <div className="address-header">
                    <FaMapMarkerAlt />
                    <span>Endereço de Entrega</span>
                  </div>
                  {userAddresses.length > 0 ? (
                    <select 
                      value={selectedAddressId || ''} 
                      onChange={(e) => {
                        const addressId = parseInt(e.target.value);
                        setSelectedAddressId(addressId);
                        calculateShipping(addressId); // Recalcular frete quando endereço mudar
                      }}
                      className="address-selector"
                    >
                      <option value="">Selecione um endereço</option>
                      {userAddresses.map((address) => (
                        <option key={address.id} value={address.id}>
                          {address.receiver_name} - {address.street}, {address.number} - {address.neighborhood}, {address.city}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <div className="no-address">
                      <p>Você não possui endereços cadastrados</p>
                      <Link to="/conta" className="btn-add-address" onClick={toggleSidebar}>
                        Cadastrar Endereço
                      </Link>
                    </div>
                  )}
                </div>

                <div className="cart-header-actions">
                  <button
                    className={`btn-continuar-pagamento btn-checkout-top ${!selectedAddressId ? 'disabled' : ''}`}
                    onClick={() => handleCheckout()}
                    disabled={!selectedAddressId}
                  >
                    Efetuar Pedido
                  </button>
                  <div className="cart-summary-top">
                    <strong>Total: R$ {(cartItems.reduce((total, item) => total + item.valor * item.quantity, 0) + shippingCost).toFixed(2)}</strong>
                    {shippingCost > 0 && (
                      <div style={{ fontSize: '12px', color: '#666', marginTop: '2px' }}>
                        (Produtos: R$ {cartItems.reduce((total, item) => total + item.valor * item.quantity, 0).toFixed(2)} + Frete: R$ {shippingCost.toFixed(2)})
                      </div>
                    )}
                  </div>
                </div>
                <ul>
                  {cartItems.map((item) => (
                    <li key={item.id} className="cart-item">
                      <div className="cart-item-details">
                        <div className="cart-item-info" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          {item.genre === 'clothe' && (
                            <img
                              src={item.image_path ? (item.image_path.startsWith('http') ? item.image_path : `${window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : 'https://rock-symphony-91f7e39d835d.herokuapp.com'}/${item.image_path}`) : 'https://via.placeholder.com/40x40?text=Camisa'}
                              alt={item.name}
                              style={{ width: 40, height: 40, objectFit: 'cover', borderRadius: 6, marginRight: 8, background: '#fff', border: '1px solid #eee' }}
                            />
                          )}
                          <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span className="item-name">{item.name}</span>
                            {item.genre === 'clothe' ? (
                              <span className="item-size">
                                Tamanho(s): {
                                  item.data
                                    ? Object.entries(item.data)
                                        .filter(([size, qty]) => qty > 0)
                                        .map(([size, qty]) => `${size.toUpperCase()} (${qty})`)
                                        .join(', ')
                                    : 'Não informado'
                                }
                              </span>
                            ) : (
                              <span className="item-artist">{item.artist || item.artist_name || 'Artista não informado'}</span>
                            )}
                          </div>
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
                  <div style={{ borderBottom: '1px solid #eee', paddingBottom: '8px', marginBottom: '8px' }}>
                    <p style={{ margin: '4px 0', display: 'flex', justifyContent: 'space-between' }}>
                      <span>Subtotal:</span>
                      <span>R$ {cartItems.reduce((total, item) => total + item.valor * item.quantity, 0).toFixed(2)}</span>
                    </p>
                    <p style={{ margin: '4px 0', display: 'flex', justifyContent: 'space-between', color: '#666' }}>
                      <span>
                        Frete: 
                        {isCalculatingShipping && <span style={{ fontSize: '12px', marginLeft: '4px' }}>(calculando...)</span>}
                      </span>
                      <span>
                        {shippingCost > 0 ? `R$ ${shippingCost.toFixed(2)}` : 'Selecione um endereço'}
                      </span>
                    </p>
                    {shippingDeliveryDays > 0 && (
                      <p style={{ margin: '2px 0', fontSize: '12px', color: '#888' }}>
                        Entrega em até {shippingDeliveryDays} dias úteis
                      </p>
                    )}
                  </div>
                  <p style={{ margin: '4px 0', fontWeight: 'bold', fontSize: '16px', display: 'flex', justifyContent: 'space-between' }}>
                    <span>Total:</span>
                    <span>R$ {(cartItems.reduce((total, item) => total + item.valor * item.quantity, 0) + shippingCost).toFixed(2)}</span>
                  </p>
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
        <Route path="/artistas" element={isLoggedIn ? <Artistas /> : <Navigate to="/login" />} />
        <Route path="/mapa-do-rock" element={<MapaDoRock />} />
        <Route path="/minhas-reservas" element={isLoggedIn ? <MeusPedidos /> : <Navigate to="/login" />} />
        <Route path="/conta" element={isLoggedIn ? <Conta onAddressUpdate={refreshAddresses} /> : <Navigate to="/login" />} />
        <Route path="/pedidos" element={isLoggedIn ? <Pedidos /> : <Navigate to="/login" />} />
        <Route path="/admin/pedidos" element={isLoggedIn ? <AdminPedidos /> : <Navigate to="/login" />} />
        <Route path="/configuracoes" element={isLoggedIn ? <Configuracoes /> : <Navigate to="/login" />} />
        <Route path="/importar-usuarios" element={isLoggedIn ? <ImportarUsuarios /> : <Navigate to="/login" />} />
        <Route path="/usuarios" element={isLoggedIn ? <UsuariosNovaTabela /> : <Navigate to="/login" />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/camisas" element={isLoggedIn ? <Camisas /> : <Navigate to="/login" />} />
        <Route path="/ver-camisas" element={<VerCamisas />} />
      </Routes>
      </main>
      
      <Footer />
    </div>
  );
}

export default App;
