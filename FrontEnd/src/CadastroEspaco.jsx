import React, { useState } from 'react';

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
    await fetch('https://ta-reservado-8e74d7e79187.herokuapp.com/api/spaces', {
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
    <div>
      <h2>Cadastrar Espaço</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="name">Nome do Espaço:</label>
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
