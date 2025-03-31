import React, { useState, useEffect } from 'react';
import { Checkbox, FormControlLabel, Button, TextField } from '@mui/material';
import { FaCheckCircle } from 'react-icons/fa'; // Ícone de sucesso

function Configuracoes() {
  const [configuracoes, setConfiguracoes] = useState({
    considerarUltimoAgendamento: false,
    tempoMaximoPagamento: '',
    intervaloMinimo: '',
    hasPagseguro: false,
    hasPagarme: false
  });
  const [showSuccess, setShowSuccess] = useState(false);

  const apiUrl = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://ta-reservado-8e74d7e79187.herokuapp.com';

  const fetchConfiguracoes = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        toast.error("Usuário não autenticado. Por favor, faça login.");
        return;
      }
      const response = await fetch(`${apiUrl}/api/configuracoes`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      let fetched_configs = {
        considerarUltimoAgendamento: data.consider_last_schedule,
        tempoMaximoPagamento: data.max_payment_time,
        intervaloMinimo: data.min_schedule_interval,
        hasPagseguro: data.has_pagseguro,
        hasPagarme: data.has_pagarme,

      }
      setConfiguracoes(fetched_configs);
    } catch (error) {
      toast.error('Erro ao carregar as configurações');
      console.error('Erro ao buscar configurações:', error);
    }
  };

  useEffect(() => {
    fetchConfiguracoes();
  }, []);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setConfiguracoes(prevConfig => ({
      ...prevConfig,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSave = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        toast.error("Usuário não autenticado. Por favor, faça login.");
        return;
      }
      await fetch(`${apiUrl}/api/configuracoes`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(configuracoes),
      });
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (error) {
      toast.error('Erro ao salvar as configurações');
      console.error('Erro ao salvar configurações:', error);
    }
  };

  return (
    <div className="configuracoes-container">
        <h2>Personalize do seu jeito</h2>
            <div>
            <FormControlLabel
                control={
                    <Checkbox
                    checked={configuracoes.considerarUltimoAgendamento}
                    onChange={handleChange}
                    name="considerarUltimoAgendamento"
                    color="primary"
                    />
                }
                label="Considerar último agendamento de qualquer espaço como data mínima para a próxima reserva"
                />
            </div>
            <div>
                <FormControlLabel
                    control={
                    <Checkbox
                        checked={configuracoes.hasPagseguro}
                        onChange={handleChange}
                        name="hasPagseguro"
                        color="primary"
                    />
                    }
                    label="Integrar pagamentos online com PagSeguro"
                />
            </div>
            <div>
                <FormControlLabel
                    control={
                    <Checkbox
                        checked={configuracoes.hasPagarme}
                        onChange={handleChange}
                        name="hasPagarme"
                        color="primary"
                    />
                    }
                    label="Integrar pagamentos online com Pagar.Me"
                />
            </div>
      <TextField
        label="Tempo máximo para pagamento antes do cancelamento automático (em horas)"
        variant="outlined"
        value={configuracoes.tempoMaximoPagamento}
        onChange={handleChange}
        name="tempoMaximoPagamento"
        fullWidth
      />
      <div className='m-top-20'>
        <TextField
          label="Intervalo mínimo entre o dia atual e o dia do agendamento do espaço (em dias)"
          variant="outlined"
          value={configuracoes.intervaloMinimo}
          onChange={handleChange}
          name="intervaloMinimo"
          fullWidth
        />
      </div>
      <div className='m-top-20'>
        <Button className="btn-save" onClick={handleSave} variant="contained">
          Salvar Configurações
        </Button>
      </div>
      {showSuccess && (
        <div className="success-message reserv-color">
          <FaCheckCircle /> Configuração salva com sucesso!
        </div>
      )}
    </div>
  );
}

export default Configuracoes;