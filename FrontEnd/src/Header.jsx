import React from 'react';
import { Link } from 'react-router-dom'; // Se estiver usando React Router 
import { FaCalendarAlt, FaHotel, FaSignOutAlt, FaUser, FaFileImport } from 'react-icons/fa'; // Importando ícones do React Icons
import { AiOutlineSchedule } from "react-icons/ai";
import { GrConfigure } from "react-icons/gr";
import './Header.css'; // Estilos do cabeçalho

function Header({ isLoggedIn, isAdmin, onLogout }) {
  return (
    <header className="header">
      <h2>Allugo</h2>
      {isLoggedIn ? (
        <div className="header-buttons">
          <Link to="/" className="space-button">
            <FaCalendarAlt /> Calendário {/* Ícone de calendário */}
          </Link>

          {!isAdmin && (
            <Link to="/minhas-reservas" className="space-button">
              <AiOutlineSchedule /> Minhas Reservas {/* Ícone de hotel */}
            </Link>
          )}
          
          {/* Mostrar botão de cadastro de espaços somente se for admin */}
          {isAdmin && (
            <>
              <Link to="/espacos" className="space-button">
                <FaHotel /> Ver Espaços {/* Ícone de hotel */}
              </Link>
              <Link to="/reservas" className="space-button">
                <AiOutlineSchedule /> Reservas {/* Ícone de hotel */}
              </Link>
              <Link to="/usuarios" className="space-button">
                <FaUser /> Usuários {/* Ícone de hotel */}
              </Link>
              <Link to="/importar-usuarios" className="space-button">
                <FaFileImport /> Importar Usuários {/* Ícone de hotel */}
              </Link>
              <Link to="/configuracoes" className="space-button">
                <GrConfigure /> Configurações {/* Ícone de hotel */}
              </Link>
            </>
          )}

          {/* Botão de logout */}
          <button onClick={onLogout} className="logout-button">
            <FaSignOutAlt /> Sair {/* Ícone de sair */}
          </button>
        </div>
      ) : (
        <></>
      )}
    </header>
  );
}

export default Header;
