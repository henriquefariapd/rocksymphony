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
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';
    // Removed the ListaUsuarios component as per the patch request
      try {

  // Removed the ListaUsuarios component as per the patch request
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
                  <td>{user.usuario || user.username || 'N/A'}</td>
                  <td>{user.email || 'N/A'}</td>
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
