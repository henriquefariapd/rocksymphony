import React, { useState } from 'react';
import './CadastroEspaco.css';

function CadastroEspaco() {
  const [nome, setNome] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    const novoEspaco = {
      name: nome,
      namespace: 'ChacaradasRosas', // Namespace fixo ou pode ser dinâmico
    };

    // Supondo que você tenha uma API para criar espaços
    // await fetch('http://localhost:8000/api/spaces', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify(novoEspaco),
    // });
    await fetch('https://rock-symphony-91f7e39d835d.herokuapp.com', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(novoEspaco),
    });


    alert('Espaço cadastrado com sucesso!');
    setNome(''); // Limpa o campo após o envio
  };

  return (
    <div className="cadastro-container">
      <h2>Cadastrar Produto</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="name">Nome do item:</label>
          <input
            type="text"
            id="name"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            required
          />
        </div>
        <button type="submit">Cadastrar</button>
      </form>
    </div>
  );
}

export default CadastroEspaco;
