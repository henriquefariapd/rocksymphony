import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { FaEdit, FaTrashAlt } from 'react-icons/fa';
import './Produtos.css';

function Produtos() {
  const [produtos, setProdutos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCadastro, setShowCadastro] = useState(false);
  const [nome, setNome] = useState('');
  const [artistId, setArtistId] = useState('');
  const [artistas, setArtistas] = useState([]);
  const [description, setDescription] = useState('');
  const [valor, setValor] = useState('');
  const [remaining, setRemaining] = useState('');
  const [referenceCode, setReferenceCode] = useState('');
  const [stamp, setStamp] = useState('');
  const [releaseYear, setReleaseYear] = useState('');
  const [country, setCountry] = useState('');
  const [imagem, setImagem] = useState(null);
  const [editingProduto, setEditingProduto] = useState(null);
  const [countries, setCountries] = useState([]);

  const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';

  const fetchProdutos = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      console.log("=== DEBUG FETCH PRODUTOS ===");
      console.log("Token:", token);
      console.log("API URL:", `${apiUrl}/api/products`);
      
      if (!token) {
        toast.error("Usuário não autenticado. Por favor, faça login.");
        return;
      }
      const response = await fetch(`${apiUrl}/api/products`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      console.log("Response status:", response.status);
      console.log("Response ok:", response.ok);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.log("Error response:", errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      console.log("Data received:", data);
      console.log("Primeiro produto:", data[0]);
      if (data[0]) {
        console.log("Artist_name do primeiro produto:", data[0].artist_name);
        console.log("Artist_id do primeiro produto:", data[0].artist_id);
      }
      setProdutos(data);
    } catch (error) {
      console.error('Erro completo ao buscar produtos:', error);
      toast.error('Erro ao carregar os produtos');
    } finally {
      setLoading(false);
    }
  };

  const fetchCountries = async () => {
    try {
      console.log("=== DEBUG FETCH COUNTRIES ===");
      console.log("API URL:", `${apiUrl}/api/countries`);
      
      const response = await fetch(`${apiUrl}/api/countries`);
      console.log("Countries response status:", response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log("Countries data:", data);
        setCountries(data.countries || []);
      } else {
        console.error('Erro no response de países:', response.status);
        setCountries([]);
      }
    } catch (error) {
      console.error('Erro ao buscar países:', error);
      setCountries([]);
    }
  };

  const fetchArtistas = async () => {
    try {
      console.log("=== DEBUG FETCH ARTISTAS ===");
      console.log("API URL:", `${apiUrl}/api/artists`);
      
      const response = await fetch(`${apiUrl}/api/artists`);
      console.log("Artists response status:", response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log("Artists data:", data);
        setArtistas(data.artists || []);
      } else {
        console.error('Erro no response de artistas:', response.status);
        setArtistas([]);
      }
    } catch (error) {
      console.error('Erro ao buscar artistas:', error);
      setArtistas([]);
    }
  };

  useEffect(() => {
    fetchProdutos();
    fetchCountries();
    fetchArtistas();
  }, []);

  const handleCadastroClick = () => {
    setShowCadastro(!showCadastro);
    setEditingProduto(null);
    setNome('');
    setArtistId('');
    setDescription('');
    setValor('');
    setRemaining('');
    setReferenceCode('');
    setStamp('');
    setReleaseYear('');
    setCountry('');
    setImagem(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("access_token");
    
    console.log("=== DEBUG SUBMIT ===");
    console.log("Token:", token);
    console.log("Nome:", nome);
    console.log("Artist ID:", artistId);
    console.log("Description:", description);
    console.log("Valor:", valor);
    console.log("Remaining:", remaining);
    console.log("Imagem:", imagem);
    console.log("EditingProduto:", editingProduto);
    
    if (!token) {
      toast.error("Usuário não autenticado. Por favor, faça login.");
      return;
    }

    try {
      const url = editingProduto
        ? `${apiUrl}/api/products/${editingProduto.id}`
        : `${apiUrl}/api/products`;

      const method = editingProduto ? 'PUT' : 'POST';

      console.log("URL:", url);
      console.log("Method:", method);

      // Tanto para POST quanto para PUT, usar FormData agora
      const formData = new FormData();
      formData.append('name', nome);
      formData.append('artist_id', artistId);
      formData.append('description', description);
      formData.append('valor', valor);
      formData.append('remaining', remaining);
      formData.append('reference_code', referenceCode);
      formData.append('stamp', stamp);
      formData.append('release_year', releaseYear || '');
      formData.append('country', country);
      
      // Adicionar imagem se existir
      if (imagem) {
        formData.append('file', imagem);
        console.log("Adicionando imagem ao FormData:", imagem.name);
      }

      console.log("Enviando FormData");
      console.log("Country value:", country);
      console.log("Countries array:", countries);
      // Log do FormData
      for (let [key, value] of formData.entries()) {
        console.log(key, value);
      }

      const response = await fetch(url, {
        method,
        headers: {
          Authorization: `Bearer ${token}`,
          // Não definir Content-Type para FormData - o browser define automaticamente
        },
        body: formData,
      });

      console.log("Response status:", response.status);
      console.log("Response headers:", response.headers);
      
      const responseData = await response.json();
      console.log("Response data:", responseData);

      if (response.ok) {
        toast.success(editingProduto ? 'Produto atualizado!' : 'Produto cadastrado!');
        setNome('');
        setArtistId('');
        setDescription('');
        setValor('');
        setRemaining('');
        setImagem(null);
        setShowCadastro(false);
        setEditingProduto(null);
        fetchProdutos();
      } else {
        toast.error(`Erro: ${responseData.detail || 'Erro desconhecido'}`);
      }
    } catch (error) {
      console.error('Erro completo:', error);
      toast.error('Erro ao salvar o produto');
    }
  };

  const handleEdit = (produto) => {
    console.log("=== DEBUG EDIT ===");
    console.log("Produto para editar:", produto);
    console.log("Artist ID do produto:", produto.artist_id);
    
    setEditingProduto(produto);
    setNome(produto.name);
    setArtistId(produto.artist_id || '');
    setDescription(produto.description);
    setValor(produto.valor);
    setRemaining(produto.remaining);
    setReferenceCode(produto.reference_code || '');
    setStamp(produto.stamp || '');
    setReleaseYear(produto.release_year || '');
    setCountry(produto.country || '');
    setImagem(null); // não carregamos imagem existente ainda
    setShowCadastro(true);
  };

  const handleDelete = async (produtoId) => {
    const confirmDelete = window.confirm('Tem certeza que deseja excluir este produto?');
    if (confirmDelete) {
      try {
        const token = localStorage.getItem("access_token");
        
        console.log("=== DEBUG DELETE ===");
        console.log("Token:", token);
        console.log("Produto ID:", produtoId);
        console.log("URL:", `${apiUrl}/api/products/${produtoId}`);
        
        if (!token) {
          toast.error("Usuário não autenticado. Por favor, faça login.");
          return;
        }
        
        const response = await fetch(`${apiUrl}/api/products/${produtoId}`, {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        
        console.log("Response status:", response.status);
        console.log("Response ok:", response.ok);
        
        if (response.ok) {
          const responseData = await response.json();
          console.log("Response data:", responseData);
          toast.success('Produto excluído com sucesso!');
          fetchProdutos();
        } else {
          const errorData = await response.json();
          console.log("Error data:", errorData);
          toast.error(`Erro: ${errorData.detail || 'Erro desconhecido'}`);
        }
      } catch (error) {
        console.error('Erro completo ao excluir:', error);
        toast.error('Erro ao excluir o produto');
      }
    }
  };

  return (
    <div>
      <h2>Gerenciar Produtos</h2>
      
      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Carregando produtos...</p>
        </div>
      ) : produtos.length === 0 ? (
        <p>Não há produtos cadastrados no momento.</p>
      ) : (
        <table className="reserv-table m-bottom-20">
        <thead>
          <tr>
            <th>Artista</th>
            <th>Álbum/CD</th>
            <th>Referência</th>
            <th>Selo</th>
            <th>Ano</th>
            <th>Valor</th>
            <th>Estoque</th>
            <th>Imagem</th>
            <th>Ações</th>
          </tr>
        </thead>
          <tbody>
            {produtos.map((produto) => (
              <tr key={produto.id}>
                <td>{produto.artist_name || produto.artist || '-'}</td>
                <td>{produto.name}</td>
                <td>{produto.reference_code || '-'}</td>
                <td>{produto.stamp || '-'}</td>
                <td>{produto.release_year || '-'}</td>
                <td>R$ {produto.valor}</td>
                <td>{produto.remaining}</td>
                <td>
                  {produto.image_path ? (
                    <img
                      src={produto.image_path.startsWith('http') ? produto.image_path : `${apiUrl}/${produto.image_path}`}
                      alt={produto.name}
                      style={{ maxWidth: '100px', maxHeight: '100px', objectFit: 'cover' }}
                    />
                  ) : (
                    'Sem imagem'
                  )}
                </td>
                <td>
                  <button className="btn-edit" onClick={() => handleEdit(produto)}>
                    <FaEdit />
                  </button>
                  <button className="btn-delete" onClick={() => handleDelete(produto.id)}>
                    <FaTrashAlt />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <button className="btn-cadastro" onClick={handleCadastroClick}>
        {showCadastro ? 'Cancelar' : 'Cadastrar Produto'}
      </button>

      {showCadastro && (
        <form onSubmit={handleSubmit} className="form-cadastro">
          <div className="form-group">
            <label htmlFor="artist">Selecione o Artista:</label>
            <select
              className="form-control"
              id="artist"
              value={artistId}
              onChange={(e) => setArtistId(e.target.value)}
              required
            >
              <option value="">Selecione um artista</option>
              {artistas.map((artist) => (
                <option key={artist.id} value={artist.id}>
                  {artist.name} ({artist.origin_country})
                </option>
              ))}
            </select>
            {artistas.length === 0 && (
              <small className="text-muted">
                Nenhum artista encontrado. <a href="/artistas">Cadastre artistas aqui</a>
              </small>
            )}
          </div>
          <div className="form-group">
            <label htmlFor="name">Nome do Álbum/CD:</label>
            <input
              className="form-control"
              type="text"
              id="name"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              required
              placeholder="Ex: Appetite for Destruction"
            />
          </div>
          <div className="form-group">
            <label htmlFor="description">Descrição:</label>
            <textarea
              className="form-control"
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              placeholder="Ex: Álbum de estreia da banda, lançado em 1987..."
              rows="3"
            />
          </div>

          <div className="form-group">
            <label htmlFor="valor">Valor (R$):</label>
            <input
              className="form-control"
              type="number"
              id="valor"
              value={valor}
              onChange={(e) => setValor(e.target.value)}
              required
              step="0.01"
              min="0"
              placeholder="Ex: 29.99"
            />
          </div>

          <div className="form-group">
            <label htmlFor="remaining">Quantidade em Estoque:</label>
            <input
              className="form-control"
              type="number"
              id="remaining"
              value={remaining}
              onChange={(e) => setRemaining(e.target.value)}
              required
              min="0"
              placeholder="Ex: 50"
            />
          </div>

          <div className="form-group">
            <label htmlFor="imagem">Imagem da Capa do CD:</label>
            <input
              className="form-control"
              type="file"
              id="imagem"
              accept="image/*"
              onChange={(e) => setImagem(e.target.files[0])}
            />
          </div>

          <div className="form-group">
            <label htmlFor="reference_code">Referência:</label>
            <input
              className="form-control"
              type="text"
              id="reference_code"
              value={referenceCode}
              onChange={(e) => setReferenceCode(e.target.value)}
              placeholder="Ex: GNR-001"
            />
          </div>

          <div className="form-group">
            <label htmlFor="stamp">Selo:</label>
            <input
              className="form-control"
              type="text"
              id="stamp"
              value={stamp}
              onChange={(e) => setStamp(e.target.value)}
              placeholder="Ex: Geffen Records"
            />
          </div>

          <div className="form-group">
            <label htmlFor="release_year">Ano de Lançamento:</label>
            <input
              className="form-control"
              type="number"
              id="release_year"
              value={releaseYear}
              onChange={(e) => setReleaseYear(e.target.value)}
              min="1900"
              max={new Date().getFullYear()}
              placeholder="Ex: 1987"
            />
          </div>

          <div className="form-group">
            <label htmlFor="country">País de Origem:</label>
            <select
              className="form-control"
              id="country"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
            >
              <option value="">Selecione um país</option>
              {countries && countries.length > 0 ? (
                countries.map((countryOption) => (
                  <option key={countryOption} value={countryOption}>
                    {countryOption}
                  </option>
                ))
              ) : (
                <option value="">Carregando países...</option>
              )}
            </select>
          </div>

          {imagem && (
            <div className="image-preview">
              <strong>Preview da Imagem:</strong><br />
              <img src={URL.createObjectURL(imagem)} alt="Preview" />
            </div>
          )}

          <button type="submit" className="btn-submit">
            {editingProduto ? 'Atualizar Produto' : 'Cadastrar Produto'}
          </button>
        </form>
      )}
    </div>
  );
}

export default Produtos;
