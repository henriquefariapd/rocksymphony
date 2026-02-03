import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { FaEdit, FaTrashAlt } from 'react-icons/fa';
import './Produtos.css';


function Camisas() {
  const [camisas, setCamisas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCadastro, setShowCadastro] = useState(false);
  const [nome, setNome] = useState('');
  const [description, setDescription] = useState('');
  const [valor, setValor] = useState('');
  const [remaining, setRemaining] = useState('');
  const [imagem, setImagem] = useState(null);
  const [editingCamisa, setEditingCamisa] = useState(null);

  const apiUrl = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';

  // Função para buscar camisas
  const fetchCamisas = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      if (!token) {
        toast.error("Usuário não autenticado. Por favor, faça login.");
        return;
      }
      const response = await fetch(`${apiUrl}/api/products/camisas`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!response.ok) {
        throw new Error("Erro ao buscar camisas");
      }
      const data = await response.json();
      setCamisas(Array.isArray(data) ? data : []);
    } catch (error) {
      toast.error('Erro ao carregar as camisas');
      console.error('Erro ao carregar camisas:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCamisas();
  }, []);

  const handleEdit = (camisa) => {
    setEditingCamisa(camisa);
    setNome(camisa.name);
    setDescription(camisa.description);
    setValor(camisa.valor);
    setRemaining(camisa.remaining);
    setImagem(null);
    setShowCadastro(true);
  };

  const handleDelete = async (camisaId) => {
    const confirmDelete = window.confirm('Tem certeza que deseja excluir esta camisa?');
    if (confirmDelete) {
      try {
        const token = localStorage.getItem("access_token");
        const response = await fetch(`${apiUrl}/api/products/${camisaId}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!response.ok) {
          throw new Error('Erro ao excluir camisa');
        }
        toast.success('Camisa excluída com sucesso!');
        setCamisas(camisas.filter(c => c.id !== camisaId));
      } catch (error) {
        toast.error('Erro ao excluir camisa');
        console.error('Erro ao excluir camisa:', error);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem("access_token");
      const formData = new FormData();
      formData.append('name', nome);
      formData.append('description', description);
      formData.append('valor', valor);
      formData.append('remaining', remaining);
      formData.append('genre', 'clothe');
      if (imagem) formData.append('file', imagem);
      let url = `${apiUrl}/api/products`;
      let method = 'POST';
      if (editingCamisa) {
        url = `${apiUrl}/api/products/${editingCamisa.id}`;
        method = 'PUT';
      }
      const response = await fetch(url, {
        method,
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });
      if (!response.ok) {
        throw new Error('Erro ao salvar camisa');
      }
      toast.success(editingCamisa ? 'Camisa atualizada!' : 'Camisa cadastrada!');
      setNome('');
      setDescription('');
      setValor('');
      setRemaining('');
      setImagem(null);
      setShowCadastro(false);
      setEditingCamisa(null);
      // Atualiza lista re-buscando do backend para garantir atualização
      await fetchCamisas();
    } catch (error) {
      toast.error('Erro ao salvar camisa');
      console.error('Erro ao salvar camisa:', error);
    }
  };

  return (
    <div className="produtos-container">
      <h1 style={{marginTop: '32px'}}>Camisas</h1>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table className="produtos-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nome</th>
              <th>Descrição</th>
              <th>Valor</th>
              <th>Estoque</th>
              <th>Imagem</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {camisas.map((camisa) => (
              <tr key={camisa.id}>
                <td>{camisa.id}</td>
                <td>{camisa.name}</td>
                <td>{camisa.description}</td>
                <td>R$ {parseFloat(camisa.valor).toFixed(2)}</td>
                <td>{camisa.remaining}</td>
                <td>
                  {camisa.image_path ? (
                    <img
                      src={camisa.image_path.startsWith('http') ? camisa.image_path : `${apiUrl}/${camisa.image_path}`}
                      alt={camisa.name}
                      style={{ maxWidth: '100px', maxHeight: '100px', objectFit: 'cover' }}
                    />
                  ) : (
                    'Sem imagem'
                  )}
                </td>
                <td>
                  <button className="btn-edit" onClick={() => handleEdit(camisa)}>
                    <FaEdit />
                  </button>
                  <button className="btn-delete" onClick={() => handleDelete(camisa.id)}>
                    <FaTrashAlt />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <button className="btn-cadastro" onClick={() => setShowCadastro(!showCadastro)}>
        {showCadastro ? 'Cancelar' : 'Cadastrar Camisa'}
      </button>
      {showCadastro && (
        <form onSubmit={handleSubmit} className="form-cadastro">
          <div className="form-group">
            <label htmlFor="name">Nome da Camisa:</label>
            <input
              className="form-control"
              type="text"
              id="name"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              required
              placeholder="Ex: Camisa Banda X"
            />
          </div>
          <div className="form-group">
            <label htmlFor="description">Descrição:</label>
            <input
              className="form-control"
              type="text"
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              placeholder="Descrição da camisa"
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
              placeholder="Ex: 59.99"
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
              placeholder="Ex: 100"
            />
          </div>
          <div className="form-group">
            <label htmlFor="imagem">Imagem da Camisa:</label>
            <input
              className="form-control"
              type="file"
              id="imagem"
              accept="image/*"
              onChange={(e) => setImagem(e.target.files[0])}
            />
          </div>
          {/* Campo genre oculto, sempre clothe */}
          <input type="hidden" name="genre" value="clothe" />
          <button type="submit" className="btn-cadastro">{editingCamisa ? 'Salvar' : 'Cadastrar'}</button>
        </form>
      )}
    </div>
  );
}

export default Camisas;
