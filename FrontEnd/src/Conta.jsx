import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { FaEdit, FaTrashAlt, FaPlus, FaMapMarkerAlt, FaStar } from 'react-icons/fa';
import './Conta.css';

function Conta({ onAddressUpdate }) {
  const [addresses, setAddresses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingAddress, setEditingAddress] = useState(null);
  const [formData, setFormData] = useState({
    cep: '',
    street: '',
    number: '',
    complement: '',
    neighborhood: '',
    city: '',
    state: '',
    country: 'Brasil',
    receiver_name: '',
    is_default: false
  });
  const [cepLoading, setCepLoading] = useState(false);

  const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';

  const fetchAddresses = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      
      if (!token) {
        toast.error("Usuário não autenticado. Por favor, faça login.");
        return;
      }

      const response = await fetch(`${apiUrl}/api/addresses`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setAddresses(data);
    } catch (error) {
      console.error('Erro ao buscar endereços:', error);
      toast.error('Erro ao carregar endereços');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAddresses();
  }, []);

  const handleCepChange = async (cep) => {
    setFormData({ ...formData, cep });
    
    // Remove caracteres não numéricos
    const cleanCep = cep.replace(/\D/g, '');
    
    if (cleanCep.length === 8) {
      setCepLoading(true);
      try {
        const response = await fetch(`${apiUrl}/api/viacep/${cleanCep}`);
        
        if (response.ok) {
          const addressData = await response.json();
          setFormData({
            ...formData,
            cep: cleanCep,
            street: addressData.street || '',
            neighborhood: addressData.neighborhood || '',
            city: addressData.city || '',
            state: addressData.state || '',
            country: addressData.country || 'Brasil'
          });
          toast.success('Endereço preenchido automaticamente!');
        } else {
          toast.error('CEP não encontrado');
        }
      } catch (error) {
        console.error('Erro ao buscar CEP:', error);
        toast.error('Erro ao buscar CEP');
      } finally {
        setCepLoading(false);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("access_token");
    
    if (!token) {
      toast.error("Usuário não autenticado. Por favor, faça login.");
      return;
    }

    try {
      const url = editingAddress 
        ? `${apiUrl}/api/addresses/${editingAddress.id}`
        : `${apiUrl}/api/addresses`;
      
      const method = editingAddress ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
        resetForm();
        fetchAddresses();
        // Atualizar endereços no componente pai (App.jsx)
        if (onAddressUpdate) onAddressUpdate();
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || 'Erro ao salvar endereço');
      }
    } catch (error) {
      console.error('Erro ao salvar endereço:', error);
      toast.error('Erro ao salvar endereço');
    }
  };

  const handleEdit = (address) => {
    setEditingAddress(address);
    setFormData({
      cep: address.cep || '',
      street: address.street || '',
      number: address.number || '',
      complement: address.complement || '',
      neighborhood: address.neighborhood || '',
      city: address.city || '',
      state: address.state || '',
      country: address.country || 'Brasil',
      receiver_name: address.receiver_name || '',
      is_default: address.is_default || false
    });
    setShowForm(true);
  };

  const handleDelete = async (addressId) => {
    const confirmDelete = window.confirm('Tem certeza que deseja excluir este endereço?');
    if (!confirmDelete) return;

    try {
      const token = localStorage.getItem("access_token");
      
      const response = await fetch(`${apiUrl}/api/addresses/${addressId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        toast.success('Endereço excluído com sucesso!');
        fetchAddresses();
        // Atualizar endereços no componente pai (App.jsx)
        if (onAddressUpdate) onAddressUpdate();
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || 'Erro ao excluir endereço');
      }
    } catch (error) {
      console.error('Erro ao excluir endereço:', error);
      toast.error('Erro ao excluir endereço');
    }
  };

  const handleSetDefault = async (addressId) => {
    try {
      const token = localStorage.getItem("access_token");
      
      const response = await fetch(`${apiUrl}/api/addresses/${addressId}/set-default`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        toast.success('Endereço definido como padrão!');
        fetchAddresses();
        // Atualizar endereços no componente pai (App.jsx)
        if (onAddressUpdate) onAddressUpdate();
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || 'Erro ao definir endereço padrão');
      }
    } catch (error) {
      console.error('Erro ao definir endereço padrão:', error);
      toast.error('Erro ao definir endereço padrão');
    }
  };

  const resetForm = () => {
    setFormData({
      cep: '',
      street: '',
      number: '',
      complement: '',
      neighborhood: '',
      city: '',
      state: '',
      country: 'Brasil',
      receiver_name: '',
      is_default: false
    });
    setEditingAddress(null);
    setShowForm(false);
  };

  const formatCep = (cep) => {
    return cep.replace(/(\d{5})(\d{3})/, '$1-$2');
  };

  return (
    <div className="conta-container">
      <h2>Minha Conta</h2>
      
      <div className="addresses-section">
        <div className="section-header">
          <h3>
            <FaMapMarkerAlt /> Endereços de Entrega
          </h3>
          <button 
            className="btn-add-address" 
            onClick={() => setShowForm(!showForm)}
          >
            <FaPlus /> {showForm ? 'Cancelar' : 'Adicionar Endereço'}
          </button>
        </div>

        {showForm && (
          <div className="address-form-container">
            <h4>{editingAddress ? 'Editar Endereço' : 'Novo Endereço'}</h4>
            <form onSubmit={handleSubmit} className="address-form">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="cep">CEP *</label>
                  <input
                    type="text"
                    id="cep"
                    value={formData.cep}
                    onChange={(e) => handleCepChange(e.target.value)}
                    placeholder="00000-000"
                    maxLength="9"
                    required
                  />
                  {cepLoading && <span className="loading-text">Buscando...</span>}
                </div>
                <div className="form-group">
                  <label htmlFor="receiver_name">Nome do Recebedor *</label>
                  <input
                    type="text"
                    id="receiver_name"
                    value={formData.receiver_name}
                    onChange={(e) => setFormData({ ...formData, receiver_name: e.target.value })}
                    placeholder="Nome completo"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="street">Rua/Avenida *</label>
                <input
                  type="text"
                  id="street"
                  value={formData.street}
                  onChange={(e) => setFormData({ ...formData, street: e.target.value })}
                  placeholder="Nome da rua"
                  required
                  readOnly={cepLoading}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="number">Número *</label>
                  <input
                    type="text"
                    id="number"
                    value={formData.number}
                    onChange={(e) => setFormData({ ...formData, number: e.target.value })}
                    placeholder="123"
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="complement">Complemento</label>
                  <input
                    type="text"
                    id="complement"
                    value={formData.complement}
                    onChange={(e) => setFormData({ ...formData, complement: e.target.value })}
                    placeholder="Apto, casa, etc."
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="neighborhood">Bairro *</label>
                  <input
                    type="text"
                    id="neighborhood"
                    value={formData.neighborhood}
                    onChange={(e) => setFormData({ ...formData, neighborhood: e.target.value })}
                    placeholder="Nome do bairro"
                    required
                    readOnly={cepLoading}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="city">Cidade *</label>
                  <input
                    type="text"
                    id="city"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    placeholder="Nome da cidade"
                    required
                    readOnly={cepLoading}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="state">Estado *</label>
                  <input
                    type="text"
                    id="state"
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                    placeholder="UF"
                    maxLength="2"
                    required
                    readOnly={cepLoading}
                  />
                </div>
              </div>

              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.is_default}
                    onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                  />
                  <span className="checkbox-text">Definir como endereço padrão</span>
                </label>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn-save">
                  {editingAddress ? 'Atualizar' : 'Salvar'} Endereço
                </button>
                <button type="button" className="logout-button" onClick={resetForm}>
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        )}

        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Carregando endereços...</p>
          </div>
        ) : addresses.length === 0 ? (
          <div className="empty-state">
            <FaMapMarkerAlt />
            <p>Você ainda não tem endereços cadastrados.</p>
            <p>Adicione um endereço para facilitar suas compras!</p>
          </div>
        ) : (
          <div className="addresses-list">
            {addresses.map((address) => (
              <div key={address.id} className={`address-card ${address.is_default ? 'default' : ''}`}>
                <div className="address-header">
                  <div className="address-title">
                    <FaMapMarkerAlt />
                    <span>{address.receiver_name}</span>
                    {address.is_default && (
                      <span className="default-badge">
                        <FaStar /> Padrão
                      </span>
                    )}
                  </div>
                  <div className="address-actions">
                    <button
                      className="btn-edit-address"
                      onClick={() => handleEdit(address)}
                      title="Editar endereço"
                    >
                      <FaEdit />
                    </button>
                    <button
                      className="btn-delete-address"
                      onClick={() => handleDelete(address.id)}
                      title="Excluir endereço"
                    >
                      <FaTrashAlt />
                    </button>
                  </div>
                </div>
                
                <div className="address-details">
                  <p className="address-text">{address.full_address}</p>
                  <p className="address-cep">CEP: {formatCep(address.cep)}</p>
                </div>

                {!address.is_default && (
                  <button
                    className="btn-set-default"
                    onClick={() => handleSetDefault(address.id)}
                  >
                    Definir como padrão
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Conta;
