import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";
import OrderStepper from "./OrderStepper";
import "./AdminPedidos.css";

const AdminPedidos = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';

  const fetchAllOrders = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      toast.error("Usuário não autenticado. Por favor, faça login.");
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/api/admin/orders`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Falha ao carregar pedidos");
      }

      const data = await response.json();
      setOrders(data);
    } catch (error) {
      console.error("Erro ao buscar pedidos:", error);
      toast.error("Erro ao carregar pedidos");
    } finally {
      setLoading(false);
    }
  };

  const updateOrderStatus = async (orderId, pending, sent) => {
    const token = localStorage.getItem("access_token");
    
    try {
      const response = await fetch(`${apiUrl}/api/orders/${orderId}/status`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ pending, sent }),
      });

      if (!response.ok) {
        throw new Error("Falha ao atualizar status do pedido");
      }

      toast.success("Status do pedido atualizado com sucesso!");
      fetchAllOrders(); // Recarregar lista
    } catch (error) {
      console.error("Erro ao atualizar status:", error);
      toast.error("Erro ao atualizar status do pedido");
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("pt-BR") + " " + date.toLocaleTimeString("pt-BR");
  };

  useEffect(() => {
    fetchAllOrders();
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
    <div className="admin-pedidos-container">
      <h2>Administração de Pedidos</h2>
      
      {orders.length === 0 ? (
        <p>Nenhum pedido encontrado.</p>
      ) : (
        <div className="orders-list">
          {orders.map((order) => (
            <div key={order.id} className="order-card">
              <div className="order-header">
                <div className="order-info">
                  <h3>Pedido #{order.id}</h3>
                  <p><strong>Cliente:</strong> {order.user_name}</p>
                  <p><strong>Data:</strong> {formatDate(order.order_date)}</p>
                  <p><strong>Total:</strong> R$ {(parseFloat(order.total_amount) || 0).toFixed(2)}</p>
                </div>
                
                <div className="status-controls">
                  <h4>Controles de Status</h4>
                  <div className="status-buttons">
                    <button
                      className={`status-btn ${order.pending ? 'active' : ''}`}
                      onClick={() => updateOrderStatus(order.id, true, false)}
                      disabled={order.pending}
                    >
                      Marcar como Pendente
                    </button>
                    
                    <button
                      className={`status-btn ${!order.pending && !order.sent ? 'active' : ''}`}
                      onClick={() => updateOrderStatus(order.id, false, false)}
                      disabled={!order.pending && !order.sent}
                    >
                      Aprovar Pagamento
                    </button>
                    
                    <button
                      className={`status-btn ${order.sent ? 'active' : ''}`}
                      onClick={() => updateOrderStatus(order.id, false, true)}
                      disabled={order.sent || order.pending}
                    >
                      Marcar como Enviado
                    </button>
                  </div>
                </div>
              </div>
              
              {/* Stepper de status do pedido */}
              <OrderStepper pending={order.pending} sent={order.sent} />
              
              <div className="order-products">
                <h4>Produtos:</h4>
                <div className="products-grid">
                  {order.products.map((product) => (
                    <div key={product.id} className="product-summary">
                      <span>{product.name} - {product.artist}</span>
                      <span>Qtd: {product.quantity}</span>
                      <span>R$ {(parseFloat(product.valor) || 0).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AdminPedidos;
