import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom"; // Para redirecionar

const Reservas = ({ apiUrl, isAdmin }) => {
  const navigate = useNavigate();
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);

  const handleGenerateReceipt = async (reservationId) => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      toast.error("Usuário não autenticado. Por favor, faça login.");
      return;
    }
  
    const apiUrl =
      window.location.hostname === "localhost"
        ? "http://localhost:8000"
        : "https://rock-symphony-91f7e39d835d.herokuapp.com";
  
    try {
      const response = await fetch(`${apiUrl}/api/generate_receipt`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ schedule_id: reservationId }),
      });
  
      if (!response.ok) {
        throw new Error("Falha ao gerar recibo");
      }
  
      // Converte a resposta para um Blob (arquivo binário)
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
  
      // Cria um link para download
      const a = document.createElement("a");
      a.href = url;
      a.download = "recibo_de_pagamento.pdf"; // Nome do arquivo ao baixar
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (error) {
      console.error("Erro ao gerar recibo:", error);
      toast.error("Erro ao gerar recibo. Tente novamente.");
    }
  };

  const handleManualPaymentCheck = async (reservationId) => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      toast.error("Usuário não autenticado. Por favor, faça login.");
      return;
    }
  
    const apiUrl =
      window.location.hostname === "localhost"
        ? "http://localhost:8000"
        : "https://rock-symphony-91f7e39d835d.herokuapp.com";
  
    try {
      const response = await fetch(`${apiUrl}/api/baixa_manual`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ schedule_id: reservationId }),
      });
  
      if (!response.ok) {
        throw new Error("Falha ao gerar recibo");
      }
      fetchReservations();
  
    } catch (error) {
      console.error("Erro ao gerar recibo:", error);
      toast.error("Erro ao gerar recibo. Tente novamente.");
    }
  };
  const fetchReservations = async () => {
    const token = localStorage.getItem("access_token");
    const apiUrl =
      window.location.hostname === "localhost"
        ? "http://localhost:8000"
        : "https://rock-symphony-91f7e39d835d.herokuapp.com";

    try {
      const response = await fetch(`${apiUrl}/api/all_schedules`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`, // Envia o token JWT no cabeçalho
        },
      });
      if (!response.ok) {
        throw new Error("Falha ao carregar reservas");
      }
      const data = await response.json();
      setReservations(data.schedules);
    } catch (error) {
      toast.error("Erro ao buscar reservas");
      console.error("Erro ao buscar reservas:", error);
    } finally {
      setLoading(false);
    }
  };
  

  useEffect(() => {
    debugger
    // Se o usuário não for admin, redireciona para outra página
    // if (!isAdmin) {
    //   navigate("/"); // ou qualquer outra rota que desejar
    //   return;
    // }
    fetchReservations();
  }, []); // Adiciona isAdmin na dependência para reavaliar a lógica

  if (loading) {
    return <p>Carregando pedidos...</p>;
  }

  return (
    <div>
      <h2>Pedidos</h2>
      {reservations.length === 0 ? (
        <p className="reserv-color">Nenhum pedido encontrado.</p>
      ) : (
        <table className="reserv-table">
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Pedido</th>
              <th>Data</th>
              <th>Status</th>
              <th>Recibo</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {reservations.map((reservation) => (
              <tr key={reservation.space_id}>
                <td>{reservation.user_name}</td>
                <td>{reservation.space_name}</td>
                <td>  {new Date(reservation.schedule_date).toLocaleDateString('pt-BR', {
                  timeZone: 'UTC', // Força o uso do fuso horário UTC para a data sem ajustes
                })}</td>
                <td>
                  {reservation.cancelled ? (
                      <span style={{ color: "black" }}>Cancelado</span>
                    ) : reservation.pending ? (
                      <span style={{ color: "red" }}>Pendente</span>
                    ) : (
                      <span style={{ color: "green" }}>Pago</span>
                    )}
                </td>
                <td>
                  <button
                    onClick={() => handleGenerateReceipt(reservation.id)}
                    disabled={reservation.pending}
                  >
                    Baixar Recibo
                  </button>
                </td>
                <td>
                  <button
                    onClick={() => handleManualPaymentCheck(reservation.id)}
                    disabled={!reservation.pending && reservation.payment_link}
                  >
                    Baixa Manual
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Reservas;
