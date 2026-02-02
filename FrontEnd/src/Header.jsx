import React from 'react';
import { Link } from 'react-router-dom'; // Se estiver usando React Router 
import { FaCalendarAlt, FaHotel, FaSignOutAlt, FaUser, FaFileImport, FaSignInAlt, FaUserCog, FaMapMarkerAlt, FaMusic } from 'react-icons/fa'; // Importando ícones do React Icons
import { AiOutlineSchedule } from "react-icons/ai";
import { GrConfigure } from "react-icons/gr";
import { GiMusicalScore } from "react-icons/gi";
import { FaHome } from "react-icons/fa";
import './Header.css'; // Estilos do cabeçalho

function Header({ isLoggedIn, isAdmin, onLogout, onLogin }) {
  return (
    <header className="header">
      <div className='d-flex'>
      <GiMusicalScore className='align-self-center' />
      <div className='m-left-10'>
        <h2>Rock Symphony</h2>
      </div>
      </div>
      {isLoggedIn ? (
        <div className="header-buttons">
          <Link to="/" className="space-button">
            <FaHome /> Home {/* Ícone de calendário */}
          </Link>
          
          <Link to="/mapa-do-rock" className="space-button">
            <FaMapMarkerAlt /> Mapa do Rock {/* Ícone de mapa */}
          </Link>

          {!isAdmin && (
            <>
              <Link to="/minhas-reservas" className="space-button">
                <AiOutlineSchedule /> Meus pedidos {/* Ícone de pedidos */}
              </Link>
              <Link to="/conta" className="space-button">
                <FaUserCog /> Conta {/* Ícone de conta/perfil */}
              </Link>
            </>
          )}
          
          {/* Mostrar botão de cadastro de espaços somente se for admin */}
          {isAdmin && (
            <>
              <Link to="/produtos" className="space-button">
                <FaHotel /> Configurar Produtos {/* Ícone de hotel */}
              </Link>
              <Link to="/camisas" className="space-button">
                <FaUser /> Camisas {/* Ícone de camisa */}
              </Link>
              <Link to="/artistas" className="space-button">
                <FaMusic /> Configurar Artistas {/* Ícone de música */}
              </Link>
              <Link to="/pedidos" className="space-button">
                <AiOutlineSchedule /> Ver pedidos {/* Ícone de hotel */}
              </Link>
              <Link to="/usuarios" className="space-button">
                <FaUser /> Usuários {/* Ícone de hotel */}
              </Link>
              {/* <Link to="/importar-usuarios" className="space-button">
                <FaFileImport /> Importar Usuários 
              </Link> */}
              {/* <Link to="/configuracoes" className="space-button">
                <GrConfigure /> Configurações 
              </Link> */}
            </>
          )}

          {/* Botão de logout */}
          <button onClick={onLogout} className="logout-button">
            <FaSignOutAlt /> Sair {/* Ícone de sair */}
          </button>
        </div>
      ) : (
        <div className="header-buttons">
          <Link to="/" className="space-button">
            <FaHome /> Home {/* Ícone de home */}
          </Link>
          <button onClick={onLogin} className="login-button">
            <FaSignInAlt /> Login {/* Ícone de login */}
          </button>
        </div>
      )}
    </header>
  );
}

export default Header;
