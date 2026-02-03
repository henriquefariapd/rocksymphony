import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { FaCartPlus } from 'react-icons/fa';
import { BiPurchaseTagAlt } from 'react-icons/bi';
import './Produtos.css';

function VerCamisas() {
  const [camisas, setCamisas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCamisa, setSelectedCamisa] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const apiUrl = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';

  useEffect(() => {
    const fetchCamisas = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${apiUrl}/api/products/camisas`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        });
        if (!response.ok) throw new Error('Erro ao buscar camisas');
        const data = await response.json();
        setCamisas(Array.isArray(data) ? data : []);
      } catch (error) {
        toast.error('Erro ao carregar as camisas');
      } finally {
        setLoading(false);
      }
    };
    fetchCamisas();
  }, []);

  // Comportamento igual ao Home.jsx
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [productIdToAddAfterLogin, setProductIdToAddAfterLogin] = useState(null);
  const [selectedSizes, setSelectedSizes] = useState({}); // { [camisaId]: 'P' | 'M' | 'G' | 'GG' }
  const [sizeWarnings, setSizeWarnings] = useState({}); // { [camisaId]: true }

  const handleAddToCart = async (camisaId) => {
    const size = selectedSizes[camisaId];
    if (!size) {
      setSizeWarnings(w => ({ ...w, [camisaId]: true }));
      return;
    }
    setSizeWarnings(w => ({ ...w, [camisaId]: false }));
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setProductIdToAddAfterLogin(camisaId);
        setShowLoginModal(true);
        return;
      }
      const response = await fetch(`${apiUrl}/api/add_product_to_cart`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ productId: camisaId, size })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Erro ao adicionar ao carrinho');
      window.location.reload();
      toast.success('Camisa adicionada ao carrinho!');
    } catch (error) {
      toast.error('Erro ao adicionar ao carrinho');
    }
  };

  const handleLoginSuccess = async () => {
    setShowLoginModal(false);
    if (productIdToAddAfterLogin) {
      setTimeout(async () => {
        await handleAddToCart(productIdToAddAfterLogin);
        setProductIdToAddAfterLogin(null);
      }, 500);
    }
  };

  const getImageUrl = (imagePath) => {
    if (!imagePath) return 'https://via.placeholder.com/100x100?text=Camisa';
    if (imagePath.startsWith('http')) return imagePath;
    return `${apiUrl}/${imagePath}`;
  };

  return (
    <div className="produtos-container">
      <h1 style={{ marginTop: '32px' }}>Camisas</h1>
      {loading ? (
        <p>Carregando...</p>
      ) : camisas.length === 0 ? (
        <p>Nenhuma camisa encontrada.</p>
      ) : (
        <div className="produtos-grid">
          {camisas.map((camisa) => (
            <div key={camisa.id} className="produto-card">
              <div className="produto-image-container">
                <img
                  src={getImageUrl(camisa.image_path)}
                  alt={camisa.name}
                  className="produto-card-image"
                  onClick={() => { setSelectedCamisa(camisa); setShowModal(true); }}
                  style={{ cursor: 'pointer' }}
                />
                {camisa.remaining && camisa.remaining < 5 && (
                  <div className="produto-badge">Últimas unidades</div>
                )}
              </div>
              <div className="produto-info">
                <h3>{camisa.name}</h3>
                <p className="produto-value">R$ {parseFloat(camisa.valor).toFixed(2)}</p>
                <p className="produto-desc">{camisa.description}</p>
              </div>
              <div className="produto-acoes">
                <button 
                  className="btn-comprar" 
                  onClick={() => { setSelectedCamisa(camisa); setShowModal(true); }}
                >
                  Ver Detalhes
                </button>
                <div style={{ marginBottom: 4 }}>
                  {sizeWarnings[camisa.id] && (
                    <div style={{ color: 'red', fontSize: '0.95em', marginBottom: 2 }}>
                      Selecione um tamanho antes de adicionar ao carrinho.
                    </div>
                  )}
                  <div
                    className="size-selector"
                    style={{
                      display: 'flex',
                      gap: '8px',
                      margin: '8px 0',
                      border: sizeWarnings[camisa.id] ? '2px solid red' : 'none',
                      borderRadius: 6,
                      padding: sizeWarnings[camisa.id] ? '4px' : 0
                    }}
                  >
                    {['P','M','G','GG'].map(sz => (
                      <button
                        key={sz}
                        className={`size-btn${selectedSizes[camisa.id] === sz ? ' selected' : ''}`}
                        onClick={() => {
                          setSelectedSizes(s => ({ ...s, [camisa.id]: sz }));
                          setSizeWarnings(w => ({ ...w, [camisa.id]: false }));
                        }}
                        type="button"
                        style={{ fontSize: '0.85rem', padding: '4px 10px', minWidth: 0, margin: 0, background: '#fff', color: '#111', border: '1px solid #ccc' }}
                      >
                        {sz}
                      </button>
                    ))}
                  </div>
                </div>
                <button 
                  className="btn-comprar" 
                  onClick={() => handleAddToCart(camisa.id)}
                  style={!selectedSizes[camisa.id] ? { opacity: 0.7, border: '1.5px solid #e74c3c' } : {}}
                >
                  <FaCartPlus />
                  +Carrinho
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      {showModal && selectedCamisa && (
        <div className="product-modal-overlay" onClick={() => setShowModal(false)}>
          <div className="product-modal" onClick={e => e.stopPropagation()}>
            <button className="modal-close-btn" onClick={() => setShowModal(false)}>
              ×
            </button>
            <div className="modal-image-section">
              <img
                src={getImageUrl(selectedCamisa.image_path)}
                alt={selectedCamisa.name}
                className="modal-product-image"
                onError={(e) => {
                  e.target.src = getImageUrl(null);
                }}
              />
              {selectedCamisa.remaining && selectedCamisa.remaining < 5 && (
                <div className="modal-product-badge">Últimas unidades</div>
              )}
              <div className="modal-actions">
                <div style={{ marginBottom: 4 }}>
                  {sizeWarnings[selectedCamisa?.id] && (
                    <div style={{ color: 'red', fontSize: '0.95em', marginBottom: 2 }}>
                      Selecione um tamanho antes de adicionar ao carrinho.
                    </div>
                  )}
                  <div
                    className="size-selector-modal"
                    style={{
                      display: 'flex',
                      gap: '8px',
                      margin: '8px 0',
                      border: sizeWarnings[selectedCamisa?.id] ? '2px solid red' : 'none',
                      borderRadius: 6,
                      padding: sizeWarnings[selectedCamisa?.id] ? '4px' : 0
                    }}
                  >
                    {['P','M','G','GG'].map(sz => (
                      <button
                        key={sz}
                        className={`size-btn${selectedSizes[selectedCamisa.id] === sz ? ' selected' : ''}`}
                        onClick={() => {
                          setSelectedSizes(s => ({ ...s, [selectedCamisa.id]: sz }));
                          setSizeWarnings(w => ({ ...w, [selectedCamisa.id]: false }));
                        }}
                        type="button"
                        style={{ fontSize: '0.85rem', padding: '4px 10px', minWidth: 0, margin: 0, background: '#fff', color: '#111', border: '1px solid #ccc' }}
                      >
                        {sz}
                      </button>
                    ))}
                  </div>
                </div>
                <button 
                  className="btn-modal-carrinho" 
                  onClick={() => handleAddToCart(selectedCamisa.id)}
                  style={!selectedSizes[selectedCamisa.id] ? { opacity: 0.7, border: '1.5px solid #e74c3c' } : {}}
                >
                  <FaCartPlus />
                  Adicionar ao Carrinho
                </button>
              </div>
            </div>
            <div className="modal-info-section">
              <h2 className="modal-product-title">{selectedCamisa.name}</h2>
              <p className="modal-product-price">R$ {parseFloat(selectedCamisa.valor).toFixed(2)}</p>
              <div className="modal-details-accordion">
                <div className="detail-item">
                  <strong>📦 Estoque:</strong>
                  <span>{selectedCamisa.remaining || 'Não informado'} unidades</span>
                </div>
                {selectedCamisa.description && (
                  <div className="detail-item description-item">
                    <strong>📝 Descrição:</strong>
                    <p>{selectedCamisa.description}</p>
                  </div>
                )}
                <div className="detail-item">
                  <strong>👕 Tamanho Selecionado:</strong>
                  <span>{selectedSizes[selectedCamisa.id] || 'Nenhum'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default VerCamisas;
