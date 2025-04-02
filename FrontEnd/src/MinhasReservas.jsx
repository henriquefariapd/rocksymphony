import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { confirmAlert } from "react-confirm-alert";
import "react-confirm-alert/src/react-confirm-alert.css";

const MinhasReservas = ({ apiUrl }) => {
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchReservations = async () => {
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
      const response = await fetch(`${apiUrl}/api/my_schedules`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
  
      if (!response.ok) {
        throw new Error("Falha ao carregar reservas");
      }
  
      const data = await response.json();
      setReservations(data);
    } catch (error) {
      toast.error("Erro ao buscar reservas");
      console.error("Erro ao buscar reservas:", error);
    } finally {
      setLoading(false);
    }
  };
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
      debugger
      const response = await fetch(`${apiUrl}/api/generate_receipt`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ 
          schedule_id: reservationId
        }),
      });
  
      if (!response.ok) {
        throw new Error("Falha ao carregar reservas");
      }
  
      const data = await response.json();
      debugger;
    } catch (error) {
      console.error("Erro ao buscar reservas:", error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchReservations();
  }, []);

  if (loading) {
    return <p>Carregando reservas...</p>;
  }

  const handlePaymentClick = (paymentLink) => {
    window.open(paymentLink, "_blank");
  };


  const handleCancelReservation = async (reservationId, pending) => {
    if (!pending) {
      confirmAlert({
        title: "Confirmação de Cancelamento",
        message:
          "O pagamento já foi realizado. O estorno será solicitado à administração e o email de cancelamento será enviado a você e ao condomínio. Deseja continuar?",
        buttons: [
          {
            label: "Sim, cancelar",
            onClick: () => executeCancelReservation(reservationId, true),
          },
          {
            label: "Não",
          },
        ],
      });
    } else {
      executeCancelReservation(reservationId);
    }
  };

  const executeCancelReservation = async (reservationId, refund = false) => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      toast.error("Usuário não autenticado. Faça login.");
      return;
    }
  
    const apiUrl =
      window.location.hostname === "localhost"
        ? "http://localhost:8000"
        : "https://rock-symphony-91f7e39d835d.herokuapp.com";
  
    try {
      const response = await fetch(`${apiUrl}/api/cancel_schedule/${reservationId}`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refund }), // Envia o valor de refund no corpo da requisição
      });
  
      if (!response.ok) {
        throw new Error("Falha ao cancelar a reserva");
      }
  
      toast.success("Reserva cancelada com sucesso!");
      fetchReservations();
    } catch (error) {
      toast.error("Erro ao cancelar reserva");
      console.error("Erro ao cancelar reserva:", error);
    }
  };

  return (
    <div>
      <h2>Minhas Reservas</h2>
      {reservations.length === 0 ? (
        <p className="reserv-color">Nenhuma reserva encontrada.</p>
      ) : (
        <table className="reserv-table">
          <thead>
            <tr>
              <th>Produto</th>
              <th>Status</th>
              <th>Pagamento</th>
              <th>Recibo</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {reservations.map((reservation) => (
              <tr key={reservation.id}>
                <td>{reservation.space_name}</td>
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
                  {reservation.pending && reservation.payment_link ? (
                    <button onClick={() => handlePaymentClick(reservation.payment_link)}>
                      Pagar agora
                    </button>
                  ) : reservation.pending ? (
                    <p>Erro ao gerar o link de pagamento</p>
                  ) : null}
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
                    onClick={() => handleCancelReservation(reservation.id, reservation.pending)}
                    disabled={reservation.cancelled}
                  >
                    Cancelar
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

export default MinhasReservas;
