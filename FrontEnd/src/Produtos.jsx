import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { FaEdit, FaTrashAlt } from 'react-icons/fa';
import './Produtos.css';

function Produtos() {
  const [produtos, setProdutos] = useState([]);
  const [showCadastro, setShowCadastro] = useState(false);
  const [nome, setNome] = useState('');
  const [artist, setArtist] = useState('');
  const [description, setDescription] = useState('');
  const [valor, setValor] = useState('');
  const [remaining, setRemaining] = useState('');
  const [imagem, setImagem] = useState(null);
  const [editingProduto, setEditingProduto] = useState(null);

  const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';

  const fetchProdutos = async () => {
    try {
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
      setProdutos(data);
    } catch (error) {
      console.error('Erro completo ao buscar produtos:', error);
      toast.error('Erro ao carregar os produtos');
    }
  };

  useEffect(() => {
    fetchProdutos();
  }, []);

  const handleCadastroClick = () => {
    setShowCadastro(!showCadastro);
    setEditingProduto(null);
    setNome('');
    setArtist('');
    setDescription('');
    setValor('');
    setRemaining('');
    setImagem(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("access_token");
    
    console.log("=== DEBUG SUBMIT ===");
    console.log("Token:", token);
    console.log("Nome:", nome);
    console.log("Artist:", artist);
    console.log("Description:", description);
    console.log("Valor:", valor);
    console.log("Remaining:", remaining);
    console.log("Imagem:", imagem);
    console.log("EditingProduto:", editingProduto);
    
    if (!token) {
      toast.error("Usuário não autenticado. Por favor, faça login.");
      return;
    }

    const formData = new FormData();
    formData.append('name', nome);
    formData.append('artist', artist);
    formData.append('description', description);
    formData.append('valor', valor);
    formData.append('remaining', remaining);
    if (imagem) {
      formData.append('file', imagem);
    }

    // Log do FormData
    console.log("FormData entries:");
    for (let [key, value] of formData.entries()) {
      console.log(key, value);
    }

    try {
      const url = editingProduto
        ? `${apiUrl}/api/products/${editingProduto.id}`
        : `${apiUrl}/api/products`;

      const method = editingProduto ? 'PUT' : 'POST';

      console.log("URL:", url);
      console.log("Method:", method);

      const response = await fetch(url, {
        method,
        headers: {
          Authorization: `Bearer ${token}`,
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
        setArtist('');
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
    setEditingProduto(produto);
    setNome(produto.name);
    setArtist(produto.artist);
    setDescription(produto.description);
    setValor(produto.valor);
    setRemaining(produto.remaining);
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
      
      {produtos.length === 0 ? (
        <p>Não há produtos cadastrados no momento.</p>
      ) : (
        <table className="reserv-table m-bottom-20">
        <thead>
          <tr>
            <th>Artista</th>
            <th>Álbum/CD</th>
            <th>Valor</th>
            <th>Estoque</th>
            <th>Imagem</th>
            <th>Ações</th>
          </tr>
        </thead>
          <tbody>
            {produtos.map((produto) => (
              <tr key={produto.id}>
                <td>{produto.artist}</td>
                <td>{produto.name}</td>
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
            <label htmlFor="artist">Nome do Artista:</label>
            <input
              className="form-control"
              type="text"
              id="artist"
              value={artist}
              onChange={(e) => setArtist(e.target.value)}
              required
              placeholder="Ex: Guns N' Roses"
            />
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
