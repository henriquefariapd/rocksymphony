import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { FaEdit, FaTrashAlt } from 'react-icons/fa';
import './Produtos.css';

function UsuariosNovaTabela() {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCadastro, setShowCadastro] = useState(false);
  const [editingUsuario, setEditingUsuario] = useState(null);
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');

  const apiUrl = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';

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
    setNome(usuario.usuario || usuario.username || '');
    setEmail(usuario.email || '');
    setShowCadastro(true);
  };

  const handleDelete = async (usuarioId) => {
    const confirmDelete = window.confirm('Tem certeza que deseja excluir este usuário?');
    if (confirmDelete) {
      try {
        const token = localStorage.getItem("access_token");
        const response = await fetch(`${apiUrl}/api/usuarios/${usuarioId}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!response.ok) {
          throw new Error('Erro ao excluir usuário');
        }
        toast.success('Usuário excluído com sucesso!');
        setUsuarios(usuarios.filter(u => u.id !== usuarioId));
      } catch (error) {
        toast.error('Erro ao excluir usuário');
        console.error('Erro ao excluir usuário:', error);
      }
    }
  };

  return (
    <div className="produtos-container">
      <h1 style={{marginTop: '32px'}}>Lista de Usuários</h1>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table className="produtos-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nome</th>
              <th>Email</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.map((usuario) => (
              <tr key={usuario.id}>
                <td>{usuario.id}</td>
                <td>{usuario.usuario || usuario.username || '-'}</td>
                <td>{usuario.email}</td>
                <td>
                  <button className="btn-edit" onClick={() => handleEdit(usuario)}>
                    <FaEdit />
                  </button>
                  <button className="btn-delete" onClick={() => handleDelete(usuario.id)}>
                    <FaTrashAlt />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default UsuariosNovaTabela;
