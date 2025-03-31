import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify'; // Usando toast para exibir mensagens de sucesso ou erro
import { FaEdit, FaTrashAlt } from 'react-icons/fa'; // Ícones de editar e excluir
import { Button } from '@mui/material';

function ListaUsuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCadastro, setShowCadastro] = useState(false);
  const [editingUsuario, setEditingUsuario] = useState(null);
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');

  const apiUrl = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://ta-reservado-8e74d7e79187.herokuapp.com';

  useEffect(() => {
    const fetchUsuarios = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          toast.error("Usuário não autenticado. Faça login.");
          return;
        }

        const response = await fetch(`${apiUrl}/api/usuarios`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (!response.ok) {
          throw new Error("Erro ao buscar usuários");
        }

        const data = await response.json();
        setUsuarios(data);
      } catch (error) {
        toast.error("Erro ao carregar usuários.");
        console.error("Erro ao carregar usuários:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsuarios();
  }, []);

  const handleEdit = (usuario) => {
    setEditingUsuario(usuario);
    setNome(usuario.username);
    setEmail(usuario.email);
    setShowCadastro(true);
  };

  const handleDelete = async (usuarioId) => {
    const confirmDelete = window.confirm('Tem certeza que deseja excluir este usuário?');
    if (confirmDelete) {
      try {
        const token = localStorage.getItem("access_token");
        const response = await fetch(`${apiUrl}/api/usuarios/${usuarioId}`, {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          toast.success("Usuário excluído com sucesso!");
          setUsuarios(usuarios.filter(user => user.id !== usuarioId));
        } else {
          toast.error("Erro ao excluir o usuário.");
        }
      } catch (error) {
        toast.error("Erro ao excluir o usuário.");
        console.error("Erro ao excluir o usuário:", error);
      }
    }
  };

  const handleCadastroClick = () => {
    setShowCadastro(!showCadastro);
    setEditingUsuario(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const novoUsuario = {
      username: nome,
      email: email,
    };

    try {
      const token = localStorage.getItem("access_token");

      if (editingUsuario) {
        await fetch(`${apiUrl}/api/usuarios/${editingUsuario.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(novoUsuario),
        });
        toast.success('Usuário atualizado com sucesso!');
      } else {
        await fetch(`${apiUrl}/api/usuarios`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(novoUsuario),
        });
        toast.success('Usuário cadastrado com sucesso!');
      }

      setNome('');
      setEmail('');
      setShowCadastro(false);
      fetchUsuarios();
    } catch (error) {
      toast.error('Erro ao salvar o usuário');
      console.error('Erro ao salvar o usuário:', error);
    }
  };

  return (
    <div>
      <h2>Lista de Usuários</h2>

      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table className="reserv-table m-bottom-20">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nome</th>
              <th>Email</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.length > 0 ? (
              usuarios.map((user) => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>{user.username}</td>
                  <td>{user.email}</td>
                  <td>
                    <div className='d-flex justify-evenly'>
                        <button onClick={() => handleEdit(user)}>
                        <FaEdit /> {/* Ícone de editar */}
                        </button>
                        <button onClick={() => handleDelete(user.id)}>
                        <FaTrashAlt /> {/* Ícone de excluir */}
                        </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4">Nenhum usuário encontrado.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      <button onClick={handleCadastroClick}>
        {showCadastro ? 'Cancelar' : 'Cadastrar Usuário'}
      </button>

      {showCadastro && (
        <form onSubmit={handleSubmit} className="form-cadastro">
          <div>
            <label htmlFor="nome">Nome do Usuário:</label>
            <input
              type="text"
              id="nome"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="email">Email:</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <button type="submit">
            {editingUsuario ? 'Atualizar Usuário' : 'Cadastrar Usuário'}
          </button>
        </form>
      )}
    </div>
  );
}

export default ListaUsuarios;
