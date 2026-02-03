import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { FaAngleDown, FaAngleUp } from "react-icons/fa";
import OrderStepper from "./OrderStepper";
import "./MeusPedidos.css";

const MeusPedidos = () => {
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
      const response = await fetch(`${apiUrl}/api/orders`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Falha ao carregar pedidos");
      }

      const data = await response.json();
      debugger
      console.log("Pedidos recebidos:", data);
      console.log("Tipo de data:", typeof data);
      console.log("É array?", Array.isArray(data));
      
      // Debug das imagens dos produtos
      if (Array.isArray(data) && data.length > 0) {
        data.forEach((order, orderIndex) => {
          console.log(`=== PEDIDO ${order.id} DEBUG ===`);
          console.log('Order completo:', order);
          if (order.products && order.products.length > 0) {
            console.log(`Produtos no pedido ${order.id}:`);
            order.products.forEach((product, productIndex) => {
              console.log(`  Produto ${productIndex + 1}:`, {
                id: product.id,
                name: product.name,
                image_path: product.image_path,
                image_path_type: typeof product.image_path,
                product_complete: product
              });
            });
          } else {
            console.log(`Pedido ${order.id} não tem produtos`);
          }
        });
      }
      
      // Garantir que data é um array
      if (Array.isArray(data)) {
        // Ordenar pedidos por data (mais recente primeiro)
        const sortedOrders = data.sort((a, b) => new Date(b.order_date) - new Date(a.order_date));
        setOrders(sortedOrders);
        
        // Expandir automaticamente o pedido mais recente se houver pedidos
        if (sortedOrders.length > 0 && !expandedOrder) {
          setExpandedOrder(sortedOrders[0].id);
        }
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

  // Função para calcular o total do pedido baseado nos produtos
  const calculateOrderTotal = (order) => {
    if (order.total_amount && !isNaN(parseFloat(order.total_amount))) {
      return parseFloat(order.total_amount);
    }
    
    // Se total_amount não estiver disponível, calcular baseado nos produtos
    if (order.products && Array.isArray(order.products)) {
      return order.products.reduce((total, product) => {
        const valor = parseFloat(product.valor) || 0;
        const quantity = parseInt(product.quantity) || 0;
        return total + (valor * quantity);
      }, 0);
    }
    
    return 0;
  };

  // Função para construir URL da imagem
  const getImageUrl = (imagePath) => {
    console.log('Construindo URL para imagem:', imagePath);
    
    if (!imagePath) {
      console.log('Imagem path vazio, usando placeholder');
      return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDE1MCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxNTAiIGhlaWdodD0iMTUwIiBmaWxsPSIjOEIxNTM4Ii8+Cjx0ZXh0IHg9Ijc1IiB5PSI4MCIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE2IiBmaWxsPSJ3aGl0ZSIgdGV4dC1hbmNob3I9Im1pZGRsZSI+QWxidW08L3RleHQ+Cjwvc3ZnPg==';
    }
    
    // Se já é uma URL completa, usar diretamente
    if (imagePath.startsWith('http')) {
      console.log('URL completa detectada:', imagePath);
      return imagePath;
    }
    
    // Se começa com /, não adicionar outra /
    if (imagePath.startsWith('/')) {
      const url = `${apiUrl}${imagePath}`;
      console.log('URL com barra inicial:', url);
      return url;
    }
    
    // Caso contrário, adicionar /
    const url = `${apiUrl}/${imagePath}`;
    console.log('URL construída:', url);
    return url;
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
    <div className="meus-pedidos-container">
      <h2>Meus Pedidos</h2>
      
      {orders.length === 0 ? (
        <p>Você ainda não fez nenhum pedido.</p>
      ) : (
        <div className="orders-list">
          {orders.map((order, index) => (
            <div key={order.id} className={`order-card ${index === 0 ? 'newest-order' : ''}`}>
              <div className="order-header" onClick={() => handleToggleOrder(order.id)}>
                <div className="order-info">
                  <h3>Pedido #{order.id}</h3>
                  <p>Data: {formatDate(order.order_date)}</p>
                  {order.shipping_cost && order.shipping_cost > 0 ? (
                    <div>
                      <p>Total: R$ {calculateOrderTotal(order).toFixed(2)}</p>
                      <p style={{ fontSize: '12px', color: '#666' }}>
                        (Produtos: R$ {(calculateOrderTotal(order) - (order.shipping_cost || 0)).toFixed(2)} + Frete: R$ {(order.shipping_cost || 0).toFixed(2)})
                      </p>
                    </div>
                  ) : (
                    <p>Total: R$ {calculateOrderTotal(order).toFixed(2)}</p>
                  )}
                  <p>Status: {order.pending ? 'Pendente' : 'Processado'}</p>
                  <small className="click-hint">Clique para ver detalhes</small>
                  
                  {/* Botão de pagamento para pedidos pendentes */}
                  {order.pending && order.payment_link && (
                    <div className="payment-section" onClick={(e) => e.stopPropagation()}>
                      <a 
                        href={order.payment_link} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="payment-button"
                      >
                        Pagar Agora
                      </a>
                    </div>
                  )}
                </div>
                <button className="toggle-button">
                  {expandedOrder === order.id ? <FaAngleUp /> : <FaAngleDown />}
                </button>
              </div>
              
              {expandedOrder === order.id && (
                <div className="order-details">
                  {/* Stepper de status do pedido */}
                  <OrderStepper pending={order.pending} sent={order.sent} />
                  
                  {/* Informações de rastreamento se o pedido foi enviado */}
                  {order.sent && order.tracking_code && (
                    <div className="tracking-section">
                      <h4>📦 Informações de Envio</h4>
                      <div className="tracking-info">
                        <p><strong>Status:</strong> Produto enviado</p>
                        <p><strong>Código de Rastreamento:</strong> {order.tracking_code}</p>
                        <a 
                          href={`https://www2.correios.com.br/sistemas/rastreamento/ctrl/ctrlRastreamento.cfm?codigo=${order.tracking_code}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="tracking-link"
                        >
                          🔍 Rastrear Pedido nos Correios
                        </a>
                      </div>
                    </div>
                  )}
                  
                  <h4>Produtos do pedido:</h4>
                  <div className="products-list">
                    {order.products.map((product) => (
                      <div key={product.id} className="product-item">
                        <img 
                          src={getImageUrl(product.image_path)}
                          alt={product.name}
                          className="product-image"
                          onError={(e) => {
                            console.log('Erro ao carregar imagem:', product.image_path);
                            console.log('URL tentada:', e.target.src);
                            e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDE1MCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxNTAiIGhlaWdodD0iMTUwIiBmaWxsPSIjOEIxNTM4Ii8+Cjx0ZXh0IHg9Ijc1IiB5PSI4MCIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE2IiBmaWxsPSJ3aGl0ZSIgdGV4dC1hbmNob3I9Im1pZGRsZSI+QWxidW08L3RleHQ+Cjwvc3ZnPg=='; // Fallback para imagem padrão
                          }}
                        />
                        <div className="product-info">
                          <h5>{product.name}</h5>
                          {product.genre !== 'clothe' && (
                            <p>Artista: {product.artist}</p>
                          )}
                          {product.genre === 'clothe' && product.data && (
                            <p>
                              Tamanhos: {
                                Object.entries(product.data)
                                  .filter(([size, qty]) => qty > 0)
                                  .map(([size, qty]) => `${size.toUpperCase()} (${qty})`)
                                  .join(', ') || 'Não informado'
                              }
                            </p>
                          )}
                          <p>Quantidade: {product.quantity}</p>
                          <p>Preço unitário: R$ {(parseFloat(product.valor) || 0).toFixed(2)}</p>
                          <p>Subtotal: R$ {((parseFloat(product.valor) || 0) * (parseInt(product.quantity) || 0)).toFixed(2)}</p>
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

export default MeusPedidos;
