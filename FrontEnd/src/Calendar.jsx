import { useState, useEffect } from "react";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import { MdEventAvailable } from "react-icons/md";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { useNavigate } from "react-router-dom"; // Para redirecionar
import "./App.css";

function App() {
  const [date, setDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [schedules, setSchedules] = useState([]); // Armazena os agendamentos
  const [availableSpaces, setAvailableSpaces] = useState([]); // Espaços disponíveis
  const navigate = useNavigate();
  const [configuracoes, setConfiguracoes] = useState({
    considerarUltimoAgendamento: false,
    tempoMaximoPagamento: '',
    intervaloMinimo: '',
    hasPagseguro: false,
    espacoTravadoAte: ''
  });

  // Definindo a URL da API conforme o ambiente
  const apiUrl =
    window.location.hostname === "localhost"
      ? "http://localhost:8000"
      : "https://ta-reservado-8e74d7e79187.herokuapp.com"; // URL para produção

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
        espacoTravadoAte: data.space_locked_untill
      }
      setConfiguracoes(fetched_configs);
    } catch (error) {
      console.error('Erro ao buscar configurações:', error);
    }
  };
  // Função para buscar os agendamentos e os espaços disponíveis do backend
  const fetchSchedulesAndSpaces = async () => {
    try {
      // Busca os agendamentos
      const token = localStorage.getItem("access_token");
      if (!token || token == 'undefined') {
        toast.error("Usuário não autenticado. Por favor, faça login.");
        return;
      }

      const scheduleResponse = await fetch(`${apiUrl}/api/schedules`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const scheduleData = await scheduleResponse.json();
      setSchedules(scheduleData); // Armazena os agendamentos no estado
      // Busca os espaços disponíveis
      const spaceResponse = await fetch(`${apiUrl}/api/spaces`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const spaceData = await spaceResponse.json();
      setAvailableSpaces(spaceData); // Armazena os espaços disponíveis no estado
    } catch (error) {
      console.error("Erro ao buscar dados:", error);
    }
  };

  useEffect(() => {
    fetchSchedulesAndSpaces(); // Busca os dados ao carregar o componente
    fetchConfiguracoes();
  }, []);

  // Função para verificar se há reservas em uma data específica
  const isDateReserved = (date) => {
    return schedules.some((schedule) => {
      let scheduleDate = new Date(schedule.schedule_date);
      scheduleDate = new Date(scheduleDate.getUTCFullYear(), scheduleDate.getUTCMonth(), scheduleDate.getUTCDate());

      return (
        scheduleDate.getDate() === date.getDate() &&
        scheduleDate.getMonth() === date.getMonth() &&
        scheduleDate.getFullYear() === date.getFullYear()
      );
    });
  };

  const isSpaceReserved = (spaceName, selectedDate) => {
    return schedules.some(
      (schedule) =>
        schedule.space_name === spaceName &&
        new Date(schedule.schedule_date).getUTCDate() === selectedDate.getDate() &&
        new Date(schedule.schedule_date).getUTCMonth() === selectedDate.getMonth() &&
        new Date(schedule.schedule_date).getUTCFullYear() === selectedDate.getFullYear()
    );
  };
  const isSpaceBlocked = (spaceName, selectedDate) => {
    return new Date(configuracoes.espacoTravadoAte[spaceName]) > selectedDate;
  };

  // Exibe o toast
  const showToast = (spaceName) => {
    toast(`${spaceName} está reservado!`);
  };

  // Função para lidar com o clique no botão "Alugar"
  const handleBookSpace = async (spaceName, selectedDate) => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token || token == 'undefined') {
        toast.error("Usuário não autenticado. Por favor, faça login.");
        return;
      }

      const response = await fetch(`${apiUrl}/schedules`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ 
          spaceName, 
          date: selectedDate.toISOString().split("T")[0]
        }),
      });
  
      const data = await response.json();
      console.log("Resposta do backend:", data);
  
      if (!response.ok) {
        throw new Error(data.detail || "Falha ao reservar o espaço");
      }
  
      // setIsModalOpen(false);
      fetchSchedulesAndSpaces();
  
      toast(`${spaceName} foi reservado com sucesso!`, {
        position: "top-right",
        autoClose: 3000,
      });
    } catch (error) {
      console.error("Erro ao reservar:", error);
      toast.error("Erro ao reservar o espaço. Tente novamente.", {
        position: "top-right",
        autoClose: 3000,
      });
    }
  };  

  // Abre o modal com detalhes do dia selecionado
  const handleTileClick = (date) => {
    setSelectedDate(date);
    setIsModalOpen(true);
  };

  // Função chamada ao passar o mouse sobre o tile
  const handleMouseEnter = (date) => {
    const reservedSchedule = schedules.find(
      (schedule) =>
      new Date(schedule.schedule_date).getUTCDate() === date.getDate() &&
      new Date(schedule.schedule_date).getUTCMonth() === date.getMonth() &&
      new Date(schedule.schedule_date).getUTCFullYear() === date.getFullYear()
    );
    if (reservedSchedule) {
      showToast(reservedSchedule.space_name); // Exibe o toast com o nome do espaço
    }
  };

  const minDate = new Date();
  minDate.setDate(minDate.getDate() + configuracoes.intervaloMinimo);

  return (
    <>
      <div>
      <Calendar
        onChange={setDate}
        value={date}
        onClickDay={handleTileClick}
        tileDisabled={({ date }) => date < minDate}
        tileContent={({ date }) => {
          const reserved = isDateReserved(date);
          return (
            <div className="text-container" onMouseEnter={() => handleMouseEnter(date)}>
              {reserved && <MdEventAvailable className="calendar-icon reserved" />}
            </div>
          );
        }}
        next2Label={null}  // Remover seta de próximo ano
        prev2Label={null}  // Remover seta de ano anterior
      />

        {/* Modal com detalhes */}
        {isModalOpen && selectedDate && (
          <div className="modal-overlay">
            <div className="modal-content">
              <h2>Detalhes do Dia {selectedDate.toLocaleDateString()}</h2>

              {/* Exibe os espaços reservados */}
              <h3>Espaços Reservados:</h3>
              {schedules
                .filter(
                  (schedule) =>
                    new Date(schedule.schedule_date).getUTCDate() === selectedDate.getDate() &&
                    new Date(schedule.schedule_date).getUTCMonth() === selectedDate.getMonth() &&
                    new Date(schedule.schedule_date).getUTCFullYear() === selectedDate.getFullYear()
                )
                .map((schedule, index) => (
                  <p className="info-row" key={index}>
                    {schedule.space_name}: <b>Alugado</b>
                    {/* Exibe o link de pagamento, se existir */}
                    {schedule.payment_link && (
                      <div>
                        <a href={schedule.payment_link} target="_blank" rel="noopener noreferrer" className="payment-link">
                          Pagar agora
                        </a>
                      </div>
                    )}
                  </p>
                ))}

              <hr className="divider" />
              <h3>Espaços Livres:</h3>
              {/* Verifica se há espaços disponíveis */}
              {availableSpaces.filter((space) => !isSpaceReserved(space.name, selectedDate)).length === 0 ? (
                <p>Não há espaços disponíveis para essa data.</p>
              ) : (
                availableSpaces
                  .map((space, index) => {
                    const isReserved = isSpaceReserved(space.name, selectedDate);
                    const isBlocked = isSpaceBlocked(space.name, selectedDate);

                    return (
                      <div className="info-row" key={index}>
                        <p>
                          {space.name}: <b>{isReserved ? "Alugado" : isBlocked ? "Bloqueado" : "Disponível"}</b>
                        </p>
                        {isBlocked && (
                          <p className="blocked-info">
                            até {new Date(configuracoes.espacoTravadoAte[space.name]).toLocaleDateString()}
                          </p>
                        )}
                        {!isReserved && !isBlocked && (
                          <button
                            className="book-button"
                            onClick={() => handleBookSpace(space.name, selectedDate)}
                          >
                            Alugar
                          </button>
                        )}
                      </div>
                    );
                  })
              )}

              <button className="close-button" onClick={() => setIsModalOpen(false)}>
                Fechar
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Container do Toast */}
      <ToastContainer
        position="bottom-center"
        autoClose={5000}    // Tempo de exibição do toast
        closeButton={true}  // Permite o botão de fechamento
        limit={1}           // Limita o número de toasts simultâneos
      />
    </>
  );
}

export default App;
