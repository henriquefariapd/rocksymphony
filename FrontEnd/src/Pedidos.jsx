import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { FaAngleDown, FaAngleUp } from "react-icons/fa";
import "./Pedidos.css";

const Pedidos = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedOrder, setExpandedOrder] = useState(null);

  const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';

  const fetchOrders = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      toast.error("Usuário não autenticado. Por favor, faça login.");
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/api/admin/all_orders`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Falha ao carregar pedidos");
      }

      const data = await response.json();
      console.log("Pedidos recebidos:", data);
      console.log("Tipo de data:", typeof data);
      console.log("É array?", Array.isArray(data));
      
      // Garantir que data é um array
      if (Array.isArray(data)) {
        setOrders(data);
      } else {
        console.error("Resposta não é um array:", data);
        setOrders([]);
      }
    } catch (error) {
      toast.error("Erro ao buscar pedidos");
      console.error("Erro ao buscar pedidos:", error);
      setOrders([]); // Garantir que orders é sempre um array
    } finally {
      setLoading(false);
    }
  };

  const handleToggleOrder = (orderId) => {
    setExpandedOrder(expandedOrder === orderId ? null : orderId);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Carregando pedidos...</p>
      </div>
    );
  }

  return (
    <div className="pedidos-container">
      <h2>Todos os Pedidos (Admin)</h2>
      
      {orders.length === 0 ? (
        <p>Nenhum pedido encontrado.</p>
      ) : (
        <div className="orders-list">
          {orders.map((order) => (
            <div key={order.id} className="order-card">
              <div className="order-header" onClick={() => handleToggleOrder(order.id)}>
                <div className="order-info">
                  <h3>Pedido #{order.id}</h3>
                  <p>Cliente: {order.user_email}</p>
                  <p>Data: {formatDate(order.order_date)}</p>
                  <p>Total: R$ {parseFloat(order.total_amount).toFixed(2)}</p>
                  <p>Status: {order.pending ? 'Pendente' : 'Processado'}</p>
                </div>
                <button className="toggle-button">
                  {expandedOrder === order.id ? <FaAngleUp /> : <FaAngleDown />}
                </button>
              </div>
              
              {expandedOrder === order.id && (
                <div className="order-details">
                  <h4>Produtos do pedido:</h4>
                  <div className="products-list">
                    {order.products.map((product) => (
                      <div key={product.id} className="product-item">
                        <img 
                          src={product.image_path?.startsWith('http') ? product.image_path : `${apiUrl}/${product.image_path}`}
                          alt={product.name}
                          className="product-image"
                        />
                        <div className="product-info">
                          <h5>{product.name}</h5>
                          <p>Artista: {product.artist}</p>
                          <p>Quantidade: {product.quantity}</p>
                          <p>Preço unitário: R$ {parseFloat(product.valor).toFixed(2)}</p>
                          <p>Subtotal: R$ {(parseFloat(product.valor) * product.quantity).toFixed(2)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Pedidos;
