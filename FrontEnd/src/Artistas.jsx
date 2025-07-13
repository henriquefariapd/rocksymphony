import React, { useState, useEffect } from 'react';
import { FaEdit, FaTrash, FaPlus, FaSave, FaTimes, FaSearch } from 'react-icons/fa';
import { toast } from 'react-toastify';
import './Artistas.css';

function Artistas() {
  const [artistas, setArtistas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingArtist, setEditingArtist] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [message, setMessage] = useState({ type: '', text: '' });
  
  const [formData, setFormData] = useState({
    name: '',
    origin_country: '',
    members: '',
    formed_year: '',
    description: '',
    genre: ''
  });

  // Lista de países para seleção
  const countries = [
    'Argentina', 'Australia', 'Austria', 'Belgium', 'Brazil', 'Canada', 
    'Denmark', 'Finland', 'France', 'Germany', 'Iceland', 'Italy', 
    'Japan', 'Netherlands', 'Norway', 'Poland', 'Portugal', 'Spain', 
    'Sweden', 'Switzerland', 'United Kingdom', 'United States'
  ];

  useEffect(() => {
    fetchArtistas();
  }, []);

  const fetchArtistas = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:8000'
        : 'https://rock-symphony-91f7e39d835d.herokuapp.com';
      
      console.log('=== DEBUG FETCH ARTISTAS ===');
      console.log('Token:', token);
      console.log('API URL:', `${apiUrl}/api/artists`);
      
      const response = await fetch(`${apiUrl}/api/artists`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (response.ok) {
        const data = await response.json();
        console.log('Response data:', data);
        setArtistas(data.artists || []);
      } else {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        showMessage('error', 'Erro ao carregar artistas');
      }
    } catch (error) {
      console.error('Erro ao buscar artistas:', error);
      showMessage('error', 'Erro ao carregar artistas');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const resetForm = () => {
    setFormData({
      name: '',
      origin_country: '',
      members: '',
      formed_year: '',
      description: '',
      genre: ''
    });
    setEditingArtist(null);
    setShowForm(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.origin_country) {
      showMessage('error', 'Nome e país de origem são obrigatórios');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      
      const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:8000'
        : 'https://rock-symphony-91f7e39d835d.herokuapp.com';
      
      const formDataToSend = new FormData();
      
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '') {
          formDataToSend.append(key, formData[key]);
        }
      });

      const url = editingArtist 
        ? `${apiUrl}/api/artists/${editingArtist.id}`
        : `${apiUrl}/api/artists`;
      
      const method = editingArtist ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formDataToSend
      });

      if (response.ok) {
        const result = await response.json();
        showMessage('success', result.message);
        fetchArtistas();
        resetForm();
      } else {
        const error = await response.json();
        showMessage('error', error.detail || 'Erro ao salvar artista');
      }
    } catch (error) {
      console.error('Erro ao salvar artista:', error);
      showMessage('error', 'Erro ao salvar artista');
    }
  };

  const handleEdit = (artist) => {
    setFormData({
      name: artist.name || '',
      origin_country: artist.origin_country || '',
      members: artist.members || '',
      formed_year: artist.formed_year || '',
      description: artist.description || '',
      genre: artist.genre || ''
    });
    setEditingArtist(artist);
    setShowForm(true);
  };

  const handleDelete = async (artist) => {
    if (!confirm(`Tem certeza que deseja excluir o artista "${artist.name}"?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:8000'
        : 'https://rock-symphony-91f7e39d835d.herokuapp.com';
      
      const response = await fetch(`${apiUrl}/api/artists/${artist.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
        fetchArtistas();
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || 'Erro ao excluir artista');
      }
    } catch (error) {
      console.error('Erro ao excluir artista:', error);
      toast.error('Erro ao excluir artista');
    }
  };

  const filteredArtistas = artistas.filter(artist =>
    artist.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    artist.origin_country.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (artist.genre && artist.genre.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return <div className="loading">Carregando artistas...</div>;
  }

  return (
    <div className="artistas-container">
      <div className="artistas-header">
        <h1>Configurar Artistas</h1>
        <button
          className="btn-primary"
          onClick={() => setShowForm(true)}
        >
          <FaPlus /> Novo Artista
        </button>
      </div>

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      {showForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>{editingArtist ? 'Editar Artista' : 'Novo Artista'}</h2>
              <button
                className="btn-close"
                onClick={resetForm}
              >
                <FaTimes />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="artist-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Nome do Artista *</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="Ex: Pink Floyd"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>País de Origem *</label>
                  <select
                    name="origin_country"
                    value={formData.origin_country}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">Selecione um país</option>
                    {countries.map(country => (
                      <option key={country} value={country}>
                        {country}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Gênero</label>
                  <input
                    type="text"
                    name="genre"
                    value={formData.genre}
                    onChange={handleInputChange}
                    placeholder="Ex: Progressive Rock"
                  />
                </div>

                <div className="form-group">
                  <label>Ano de Formação</label>
                  <input
                    type="number"
                    name="formed_year"
                    value={formData.formed_year}
                    onChange={handleInputChange}
                    placeholder="Ex: 1965"
                    min="1900"
                    max={new Date().getFullYear()}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Membros</label>
                <textarea
                  name="members"
                  value={formData.members}
                  onChange={handleInputChange}
                  placeholder="Ex: David Gilmour, Roger Waters, Nick Mason, Richard Wright"
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label>Descrição</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Descrição da banda..."
                  rows="4"
                />
              </div>

              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={resetForm}>
                  <FaTimes /> Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  <FaSave /> {editingArtist ? 'Atualizar' : 'Salvar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="search-container">
        <div className="search-box">
          <FaSearch />
          <input
            type="text"
            placeholder="Buscar por nome, país ou gênero..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="artistas-list">
        {filteredArtistas.length === 0 ? (
          <div className="no-results">
            {searchTerm ? 'Nenhum artista encontrado' : 'Nenhum artista cadastrado'}
          </div>
        ) : (
          <div className="artistas-grid">
            {filteredArtistas.map(artist => (
              <div key={artist.id} className="artist-card">
                <div className="artist-header">
                  <h3>{artist.name}</h3>
                  <div className="artist-actions">
                    <button
                      className="btn-edit"
                      onClick={() => handleEdit(artist)}
                      title="Editar"
                    >
                      <FaEdit />
                    </button>
                    <button
                      className="btn-delete"
                      onClick={() => handleDelete(artist)}
                      title="Excluir"
                    >
                      <FaTrash />
                    </button>
                  </div>
                </div>

                <div className="artist-info">
                  <p><strong>País:</strong> {artist.origin_country}</p>
                  {artist.genre && <p><strong>Gênero:</strong> {artist.genre}</p>}
                  {artist.formed_year && <p><strong>Formação:</strong> {artist.formed_year}</p>}
                  {artist.members && (
                    <p><strong>Membros:</strong> {artist.members}</p>
                  )}
                  {artist.description && (
                    <p className="artist-description">{artist.description}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Artistas;
