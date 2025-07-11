import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { FaEdit, FaTrashAlt } from 'react-icons/fa'; // Importando os ícones
import { FaCartPlus } from "react-icons/fa";
import { BiPurchaseTagAlt } from "react-icons/bi";
import { FaAngleDown, FaAngleUp } from "react-icons/fa";


function Home() {
  const [produtos, setProdutos] = useState([]);
  const [showCadastro, setShowCadastro] = useState(false);
  const [nome, setNome] = useState('');
  const [valor, setValor] = useState('');
  const [minDays, setMinDays] = useState('');
  const [editingEspaco, setEditingEspaco] = useState(null);
  const [expandedProduct, setExpandedProduct] = useState(null);

  const handleToggleDescription = (productId) => {
    setExpandedProduct(expandedProduct === productId ? null : productId);
  };

  const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';

  const fetchEspacos = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        toast.error("Usuário não autenticado. Por favor, faça login.");
        return;
      }
      
      console.log("[DEBUG] Buscando produtos...");
      console.log("[DEBUG] URL:", `${apiUrl}/api/products`);
      console.log("[DEBUG] Token:", token ? "presente" : "ausente");
      
      const response = await fetch(`${apiUrl}/api/products`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
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
      
      setProdutos(data);
    } catch (error) {
      console.error('[DEBUG] Erro ao buscar produtos:', error);
      toast.error('Erro ao carregar os produtos');
    }
  };

  useEffect(() => {
    fetchEspacos();
  }, []);

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
      fetchEspacos();
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
        toast.error("Usuário não autenticado. Por favor, faça login.");
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
        fetchEspacos();
      } catch (error) {
        toast.error('Erro ao excluir o espaço');
        console.error('Erro ao excluir o espaço:', error);
      }
    }
  };

  return (
    <div>
      <h2>Catálogo</h2>

      {produtos.length === 0 ? (
        <p>Não há CDs cadastrados no momento.</p>
      ) : (
        <div className="produtos-grid">
          {produtos.map((espaco) => (
            <div key={espaco.id} className="produto-card">
              <img
                src={`${apiUrl}/${espaco.image_path}`}
                alt={espaco.name}
                className="produto-imagem"
              />
              <div className="produto-info">
                <h3>{espaco.name} - {espaco.artist}</h3>
                {/* Accordion de descrição */}
                <div className="accordion-container">
                  <p className="produto-value">R$ {espaco.valor}</p>
                  <button 
                    className="accordion-toggle"
                    onClick={() => handleToggleDescription(espaco.id)}
                  >
                    {expandedProduct === espaco.id ? (
                      <FaAngleUp />  // Ícone de seta para cima quando expandido
                    ) : (
                      <FaAngleDown />  // Ícone de seta para baixo quando recolhido
                    )}
                    {expandedProduct === espaco.id ? " Fechar" : " Ver descrição"}
                  </button>
                  {expandedProduct === espaco.id && (
                    <p className="produto-description">{espaco.description}</p>
                  )}
                </div>
              </div>
              <div className="produto-acoes">
                <button className="btn-comprar">
                  <BiPurchaseTagAlt /> Comprar
                </button>
                <button className="btn-comprar" onClick={() => handleAddtoCart(espaco.id)}>
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
