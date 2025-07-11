// TestPasswordReset.jsx
import React, { useState } from 'react';
import axios from 'axios';

function TestPasswordReset() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const apiUrl = "http://127.0.0.1:8000";
      const response = await axios.post(`${apiUrl}/auth/reset-password`, {
        email: email
      });
      
      setMessage('Email de recuperação enviado com sucesso!');
      setError('');
    } catch (err) {
      setError('Erro ao enviar email de recuperação');
      setMessage('');
      console.error(err);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '400px', margin: '0 auto' }}>
      <h2>Test Password Reset</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '10px' }}>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <button type="submit" style={{ width: '100%', padding: '10px' }}>
          Enviar Email de Recuperação
        </button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default TestPasswordReset;
