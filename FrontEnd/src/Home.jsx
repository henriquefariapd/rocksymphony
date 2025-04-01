import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { FaEdit, FaTrashAlt } from 'react-icons/fa'; // Importando os ícones
import { FaCartPlus } from "react-icons/fa";
import { BiPurchaseTagAlt } from "react-icons/bi";

function Home() {
  const [espacos, setEspacos] = useState([]);
  const [showCadastro, setShowCadastro] = useState(false);
  const [nome, setNome] = useState('');
  const [valor, setValor] = useState('');
  const [minDays, setMinDays] = useState('');
  const [editingEspaco, setEditingEspaco] = useState(null);

  const apiUrl = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://ta-reservado-8e74d7e79187.herokuapp.com';

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
      <h2>Produtos Disponíveis</h2>
      
      {espacos.length === 0 ? (
        <p>Não há espaços cadastrados no momento.</p>
      ) : (
        <table className="reserv-table m-bottom-20 m-0-auto">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Valor</th>
              <th>Unidades Restantes</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {espacos.map((espaco) => (
              <tr key={espaco.id}>
                <td>{espaco.name}</td>
                <td>R$ {espaco.valor}</td>
                <td>{espaco.min_days}</td>
                <td>
                  <button className="btn-edit" onClick={() => handleEdit(espaco)}>
                    <FaCartPlus /> {/* Ícone de lápis */}
                  </button>
                  <button className="btn-delete" onClick={() => handleDelete(espaco.id)}>
                    <BiPurchaseTagAlt /> {/* Ícone de lixeira */}
                    comprar
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

export default Home;
