import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { FaEdit, FaTrashAlt } from 'react-icons/fa';

function Espacos() {
  const [espacos, setEspacos] = useState([]);
  const [showCadastro, setShowCadastro] = useState(false);
  const [nome, setNome] = useState('');
  const [valor, setValor] = useState('');
  const [remaining, setRemaining] = useState('');
  const [imagem, setImagem] = useState(null);
  const [editingEspaco, setEditingEspaco] = useState(null);

  const apiUrl = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';

  const fetchEspacos = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        toast.error("Usuário não autenticado. Por favor, faça login.");
        return;
      }
      const response = await fetch(`${apiUrl}/api/spaces`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setEspacos(data);
    } catch (error) {
      toast.error('Erro ao carregar os espaços');
      console.error('Erro ao buscar espaços:', error);
    }
  };

  useEffect(() => {
    fetchEspacos();
  }, []);

  const handleCadastroClick = () => {
    setShowCadastro(!showCadastro);
    setEditingEspaco(null);
    setNome('');
    setValor('');
    setRemaining('');
    setImagem(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("access_token");
    if (!token) {
      toast.error("Usuário não autenticado. Por favor, faça login.");
      return;
    }

    const formData = new FormData();
    formData.append('name', nome);
    formData.append('valor', valor);
    formData.append('remaining', remaining);
    if (imagem) {
      formData.append('image', imagem);
    }

    try {
      const url = editingEspaco
        ? `${apiUrl}/spaces/${editingEspaco.id}`
        : `${apiUrl}/spaces`;

      const method = editingEspaco ? 'PUT' : 'POST';

      await fetch(url, {
        method,
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      toast.success(editingEspaco ? 'Espaço atualizado!' : 'Espaço cadastrado!');
      setNome('');
      setValor('');
      setRemaining('');
      setImagem(null);
      setShowCadastro(false);
      setEditingEspaco(null);
      fetchEspacos();
    } catch (error) {
      toast.error('Erro ao salvar o espaço');
      console.error('Erro ao salvar o espaço:', error);
    }
  };

  const handleEdit = (espaco) => {
    setEditingEspaco(espaco);
    setNome(espaco.name);
    setValor(espaco.valor);
    setRemaining(espaco.remaining);
    setImagem(null); // não carregamos imagem existente ainda
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
      <h2>Produtos Disponíveis</h2>
      
      {espacos.length === 0 ? (
        <p>Não há espaços cadastrados no momento.</p>
      ) : (
        <table className="reserv-table m-bottom-20">
        <thead>
          <tr>
            <th>Artista</th>
            <th>Item</th>
            <th>Valor</th>
            <th>Estoque</th>
            <th>Imagem</th> {/* <- nova coluna */}
            <th>Ações</th>
          </tr>
        </thead>
          <tbody>
            {espacos.map((espaco) => (
              <tr key={espaco.id}>
                <td>{espaco.name}</td>
                <td>{espaco.name}</td>
                <td>R$ {espaco.valor}</td>
                <td>{espaco.remaining}</td>
                <td>
                  {espaco.image_url ? (
                    <img
                      src={`${apiUrl}${espaco.image_url}`}
                      alt={espaco.name}
                      style={{ maxWidth: '100px', maxHeight: '100px', objectFit: 'cover' }}
                    />
                  ) : (
                    'Sem imagem'
                  )}
                </td>
                <td>
                  <button className="btn-edit" onClick={() => handleEdit(espaco)}>
                    <FaEdit />
                  </button>
                  <button className="btn-delete" onClick={() => handleDelete(espaco.id)}>
                    <FaTrashAlt />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <button className="btn-cadastro" onClick={handleCadastroClick}>
        {showCadastro ? 'Cancelar' : 'Cadastrar'}
      </button>

      {showCadastro && (
        <form onSubmit={handleSubmit} className="form-cadastro">
          <div className="form-group">
            <label htmlFor="name">Nome do Item:</label>
            <input
              className="form-control"
              type="text"
              id="name"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="valor">Valor:</label>
            <input
              className="form-control"
              type="number"
              id="valor"
              value={valor}
              onChange={(e) => setValor(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="remaining">Estoque:</label>
            <input
              className="form-control"
              type="number"
              id="remaining"
              value={remaining}
              onChange={(e) => setRemaining(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="imagem">Imagem do Produto:</label>
            <input
              className="form-control"
              type="file"
              id="imagem"
              accept="image/*"
              onChange={(e) => setImagem(e.target.files[0])}
            />
          </div>

          {imagem && (
            <div style={{ marginTop: '10px' }}>
              <strong>Preview:</strong><br />
              <img src={URL.createObjectURL(imagem)} alt="Preview" style={{ maxWidth: '200px' }} />
            </div>
          )}

          <button type="submit" className="btn-submit">
            {editingEspaco ? 'Atualizar Produto' : 'Cadastrar Produto'}
          </button>
        </form>
      )}
    </div>
  );
}

export default Espacos;
