import React from 'react';
import { Link } from 'react-router-dom'; // Se estiver usando React Router 
import { FaCalendarAlt, FaHotel, FaSignOutAlt, FaUser, FaFileImport } from 'react-icons/fa'; // Importando ícones do React Icons
import { AiOutlineSchedule } from "react-icons/ai";
import { GrConfigure } from "react-icons/gr";
import { GiMusicalScore } from "react-icons/gi";
import { FaHome } from "react-icons/fa";
import './Header.css'; // Estilos do cabeçalho

function Header({ isLoggedIn, isAdmin, onLogout }) {
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

          {!isAdmin && (
            <Link to="/minhas-reservas" className="space-button">
              <AiOutlineSchedule /> Meus pedidos {/* Ícone de hotel */}
            </Link>
          )}
          
          {/* Mostrar botão de cadastro de espaços somente se for admin */}
          {isAdmin && (
            <>
              <Link to="/produtos" className="space-button">
                <FaHotel /> Configurar Produtos {/* Ícone de hotel */}
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
        <></>
      )}
    </header>
  );
}

export default Header;
