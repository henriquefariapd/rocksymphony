import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { FaEdit, FaTrashAlt } from 'react-icons/fa'; // Importando os ícones
import { FaCartPlus } from "react-icons/fa";
import { BiPurchaseTagAlt } from "react-icons/bi";
import { FaAngleDown, FaAngleUp } from "react-icons/fa";
import LoginModal from './LoginModal';
import './Home.css';


function Home() {
  const [produtos, setProdutos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCadastro, setShowCadastro] = useState(false);
  const [nome, setNome] = useState('');
  const [valor, setValor] = useState('');
  const [minDays, setMinDays] = useState('');
  const [editingEspaco, setEditingEspaco] = useState(null);
  const [expandedProduct, setExpandedProduct] = useState(null);
  const [showLoginModal, setShowLoginModal] = useState(false);
  
  // Estados para busca e filtros
  const [searchQuery, setSearchQuery] = useState('');
  const [countryFilter, setCountryFilter] = useState('');
  const [stampFilter, setStampFilter] = useState('');
  const [yearFilter, setYearFilter] = useState('');
  const [filters, setFilters] = useState({ countries: [], stamps: [], release_years: [] });
  const [filteredProdutos, setFilteredProdutos] = useState([]);
  const [allCountries, setAllCountries] = useState([]);

  // Função helper para construir URL da imagem
  const getImageUrl = (imagePath) => {
    if (!imagePath) {
      // SVG placeholder inline para CD
      return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjUwIiBoZWlnaHQ9IjI1MCIgdmlld0JveD0iMCAwIDI1MCAyNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyNTAiIGhlaWdodD0iMjUwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9IjEyNSIgY3k9IjEyNSIgcj0iODAiIGZpbGw9IiMyMzI5MkYiLz4KPGNpcmNsZSBjeD0iMTI1IiBjeT0iMTI1IiByPSI2MCIgZmlsbD0iIzM3NDE0RSIvPgo8Y2lyY2xlIGN4PSIxMjUiIGN5PSIxMjUiIHI9IjEwIiBmaWxsPSIjRjNGNEY2Ii8+Cjx0ZXh0IHg9IjEyNSIgeT0iMjIwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjNkI3Mjg4IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiPkNEIFJvY2s8L3RleHQ+Cjwvc3ZnPg==';
    }
    if (imagePath.startsWith('http')) {
      return imagePath; // URL completa
    }
    return `${apiUrl}/${imagePath}`; // URL relativa
  };

  const handleToggleDescription = (productId) => {
    setExpandedProduct(expandedProduct === productId ? null : productId);
  };

  const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';

  const fetchProdutos = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      
      console.log("[DEBUG] Buscando produtos...");
      console.log("[DEBUG] URL:", `${apiUrl}/api/products`);
      console.log("[DEBUG] Token:", token ? "presente" : "ausente");
      
      // Preparar headers - incluir token apenas se existir
      const headers = {
        "Content-Type": "application/json"
      };
      
      if (token && token !== 'undefined') {
        headers.Authorization = `Bearer ${token}`;
      }
      
      const response = await fetch(`${apiUrl}/api/products`, {
        method: "GET",
        headers: headers,
      });
      
      console.log("[DEBUG] Response status:", response.status);
      console.log("[DEBUG] Response ok:", response.ok);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.log("[DEBUG] Error response:", errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      console.log("[DEBUG] Produtos recebidos:", data);
      console.log("[DEBUG] Número de produtos:", data.length);
      
      // Verificar se data é um array
      if (Array.isArray(data)) {
        setProdutos(data);
        setFilteredProdutos(data); // Inicializar produtos filtrados
      } else {
        console.error("[DEBUG] Produtos recebidos não são um array:", data);
        setProdutos([]);
        setFilteredProdutos([]);
        toast.error('Erro no formato dos dados dos produtos');
      }
    } catch (error) {
      console.error('[DEBUG] Erro ao buscar produtos:', error);
      toast.error('Erro ao carregar os produtos');
    } finally {
      setLoading(false);
    }
  };

  // Função para buscar filtros disponíveis
  const fetchFilters = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/products/filters`);
      if (response.ok) {
        const data = await response.json();
        setFilters(data);
      }
    } catch (error) {
      console.error('Erro ao buscar filtros:', error);
    }
  };

  // Função para buscar países disponíveis
  const fetchCountries = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/countries`);
      if (response.ok) {
        const data = await response.json();
        setAllCountries(data.countries);
      }
    } catch (error) {
      console.error('Erro ao buscar países:', error);
    }
  };

  // Função para aplicar filtros
  const applyFilters = async () => {
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append('q', searchQuery);
      if (countryFilter) params.append('country', countryFilter);
      if (stampFilter) params.append('stamp', stampFilter);
      if (yearFilter) params.append('release_year', yearFilter);

      const token = localStorage.getItem("access_token");
      const headers = { "Content-Type": "application/json" };
      if (token && token !== 'undefined') {
        headers.Authorization = `Bearer ${token}`;
      }

      console.log("[DEBUG] Aplicando filtros:", {
        searchQuery, countryFilter, stampFilter, yearFilter
      });

      const response = await fetch(`${apiUrl}/api/products/search?${params.toString()}`, {
        method: "GET",
        headers: headers,
      });

      console.log("[DEBUG] Resposta dos filtros status:", response.status);

      if (response.ok) {
        const data = await response.json();
        console.log("[DEBUG] Dados de busca recebidos:", data);
        
        // Verificar se data é um array
        if (Array.isArray(data)) {
          setFilteredProdutos(data);
        } else {
          console.error("[DEBUG] Resposta da busca não é um array:", data);
          setFilteredProdutos([]);
          toast.error('Erro no formato dos dados de busca');
        }
      } else {
        console.error("[DEBUG] Erro na resposta da busca:", response.status);
        const errorText = await response.text();
        console.error("[DEBUG] Texto do erro:", errorText);
        setFilteredProdutos([]);
        toast.error('Erro ao buscar produtos');
      }
    } catch (error) {
      console.error('Erro ao aplicar filtros:', error);
      setFilteredProdutos([]);
      toast.error('Erro ao aplicar filtros');
    }
  };

  // Função para limpar filtros
  const clearFilters = () => {
    setSearchQuery('');
    setCountryFilter('');
    setStampFilter('');
    setYearFilter('');
    // Garantir que produtos seja um array antes de definir filteredProdutos
    if (Array.isArray(produtos)) {
      setFilteredProdutos(produtos);
    } else {
      setFilteredProdutos([]);
    }
  };

  useEffect(() => {
    fetchProdutos();
    fetchFilters();
    fetchCountries();
  }, []);

  // UseEffect para aplicar filtros quando mudarem
  useEffect(() => {
    if (searchQuery || countryFilter || stampFilter || yearFilter) {
      applyFilters();
    } else {
      // Garantir que produtos seja um array antes de definir filteredProdutos
      if (Array.isArray(produtos)) {
        setFilteredProdutos(produtos);
      } else {
        setFilteredProdutos([]);
      }
    }
  }, [searchQuery, countryFilter, stampFilter, yearFilter, produtos]);

  const handleCadastroClick = () => {
    setShowCadastro(!showCadastro);
    setEditingEspaco(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("access_token");
    if (!token) {
      toast.error("Usuário não autenticado. Por favor, faça login.");
      return;
    }

    const novoEspaco = {
      name: nome,
      valor: valor,
      min_days: minDays,
    };

    try {
      if (editingEspaco) {
        await fetch(`${apiUrl}/spaces/${editingEspaco.id}`, {
          method: 'PUT',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(novoEspaco),
        });
        toast.success('Espaço atualizado com sucesso!');
      } else {
        await fetch(`${apiUrl}/spaces`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(novoEspaco),
        });
        toast.success('Espaço cadastrado com sucesso!');
      }

      setNome('');
      setValor('');
      setMinDays('');
      setShowCadastro(false);
      setEditingEspaco(null);
      fetchProdutos();
    } catch (error) {
      toast.error('Erro ao salvar o espaço');
      console.error('Erro ao salvar o espaço:', error);
    }
  };

  const handlePurchase = async (productName) => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token || token == 'undefined') {
        toast.error("Usuário não autenticado. Por favor, faça login.");
        return;
      }

      const response = await fetch(`${apiUrl}/orders`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ 
          productName
        }),
      });
  
      const data = await response.json();
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

  const handleAddtoCart = async (productId) => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token || token == 'undefined') {
        // Mostrar modal de login ao invés de toast
        setShowLoginModal(true);
        return;
      }

      const response = await fetch(`${apiUrl}/api/add_product_to_cart`, {
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
        throw new Error(data.detail || "Falha ao adicionar produto ao carrinho");
      }
  
      toast.success("Produto adicionado ao carrinho com sucesso!");
    } catch (error) {
      console.error("Erro ao adicionar ao carrinho:", error);
      toast.error("Erro ao adicionar produto ao carrinho. Tente novamente.");
    }
  }; 

  const handleEdit = (espaco) => {
    setEditingEspaco(espaco);
    setNome(espaco.name);
    setValor(espaco.valor);
    setMinDays(espaco.min_days);
    setShowCadastro(true);
  };

  const handleDelete = async (espacoId) => {
    const confirmDelete = window.confirm('Tem certeza que deseja excluir este espaço?');
    if (confirmDelete) {
      try {
        await fetch(`${apiUrl}/spaces/${espacoId}`, {
          method: 'DELETE',
        });
        toast.success('Espaço excluído com sucesso!');
        fetchProdutos();
      } catch (error) {
        toast.error('Erro ao excluir o espaço');
        console.error('Erro ao excluir o espaço:', error);
      }
    }
  };

  return (
    <div>

      {/* Barra de busca e filtros */}
      <div className="search-filters-container">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Buscar por nome do CD ou artista..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="filters-row">
          <select
            value={stampFilter}
            onChange={(e) => setStampFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Todos os Selos</option>
            {filters.stamps && filters.stamps.map(stamp => (
              <option key={stamp} value={stamp}>{stamp}</option>
            ))}
          </select>

          <select
            value={yearFilter}
            onChange={(e) => setYearFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Todos os Anos</option>
            {filters.release_years && filters.release_years.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>

          {/* <select
            value={countryFilter}
            onChange={(e) => setCountryFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Todos os Países</option>
            {allCountries && allCountries.map(country => (
              <option key={country} value={country}>{country}</option>
            ))}
          </select> */}

          <button onClick={clearFilters} className="clear-filters-btn">
            Limpar Filtros
          </button>
        </div>
      </div>

      {/* Modal de Login */}
      <LoginModal 
        isOpen={showLoginModal} 
        onClose={() => setShowLoginModal(false)} 
      />

      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Carregando produtos...</p>
        </div>
      ) : !Array.isArray(filteredProdutos) ? (
        <div className="error-container">
          <p>Erro ao carregar produtos. Recarregue a página.</p>
          <button onClick={() => window.location.reload()}>Recarregar</button>
        </div>
      ) : filteredProdutos.length === 0 ? (
        <div className="no-results">
          <p>
            {searchQuery || countryFilter || stampFilter || yearFilter 
              ? `Nenhum resultado encontrado para sua busca.`
              : 'Não há CDs cadastrados no momento.'
            }
          </p>
          {(searchQuery || countryFilter || stampFilter || yearFilter) && (
            <button onClick={clearFilters} className="clear-filters-btn">
              Limpar Filtros
            </button>
          )}
        </div>
      ) : (
        <div className="produtos-grid">
          {filteredProdutos.map((produto) => (
            <div key={produto.id} className="produto-card">
              <img
                src={getImageUrl(produto.image_path)}
                alt={produto.name}
                className="produto-card-image"
                onError={(e) => {
                  e.target.src = getImageUrl(null); // Usar placeholder se a imagem falhar
                }}
              />
              <div className="produto-info">
                <h3>{produto.name}</h3>
                <p className="produto-artist">{produto.artist_name || produto.artist || 'Artista não informado'}</p>
                
                {/* Novos campos */}
                <div className="produto-details">
                  {produto.reference_code && (
                    <p className="produto-reference">Ref: {produto.reference_code}</p>
                  )}
                  {produto.stamp && (
                    <p className="produto-stamp">Selo: {produto.stamp}</p>
                  )}
                  {produto.release_year && (
                    <p className="produto-year">Ano: {produto.release_year}</p>
                  )}
                </div>
                
                {/* Accordion de descrição */}
                <div className="accordion-container">
                  <p className="produto-value">R$ {produto.valor}</p>
                  <button 
                    className="accordion-toggle"
                    onClick={() => handleToggleDescription(produto.id)}
                  >
                    {expandedProduct === produto.id ? (
                      <FaAngleUp />  // Ícone de seta para cima quando expandido
                    ) : (
                      <FaAngleDown />  // Ícone de seta para baixo quando recolhido
                    )}
                    {expandedProduct === produto.id ? " Fechar" : " Ver descrição"}
                  </button>
                  {expandedProduct === produto.id && (
                    <p className="produto-description">{produto.description}</p>
                  )}
                </div>
              </div>
              <div className="produto-acoes">
                <button className="btn-comprar">
                  <BiPurchaseTagAlt /> Comprar
                </button>
                <button className="btn-comprar" onClick={() => handleAddtoCart(produto.id)}>
                  <FaCartPlus /> Adicionar ao carrinho
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
  
}

export default Home;
