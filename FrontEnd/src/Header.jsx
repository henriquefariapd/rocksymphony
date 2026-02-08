
import React from 'react';
import { Link } from 'react-router-dom';
import { FaHotel, FaSignOutAlt, FaUser, FaSignInAlt, FaUserCog, FaMapMarkerAlt, FaMusic, FaTshirt } from 'react-icons/fa';
import { AiOutlineSchedule } from 'react-icons/ai';
import { GiMusicalScore } from 'react-icons/gi';
import { FaHome } from 'react-icons/fa';
import './Header.css';

function Header({ isLoggedIn, isAdmin, onLogout, onLogin }) {
  return (
    <header className="header">
      <div className="header-left d-flex hide-mobile">
        <GiMusicalScore className="align-self-center" />
        <div className="m-left-10">
          <h2>Rock Symphony</h2>
        </div>
      </div>
      <nav className="header-buttons">
        <Link to="/" className="space-button">
          <FaHome /> <span className="button-text">Home</span>
        </Link>
        <Link to="/ver-camisas" className="space-button">
          <FaTshirt className="icon-camisa" />
          <span className="button-text">Camisas</span>
        </Link>
        <Link to="/mapa-do-rock" className="space-button">
          <FaMapMarkerAlt /> <span className="button-text">Mapa do Rock</span>
        </Link>
        {isLoggedIn && !isAdmin && (
          <>
            <Link to="/minhas-reservas" className="space-button">
              <AiOutlineSchedule /> <span className="button-text">Meus pedidos</span>
            </Link>
            <Link to="/conta" className="space-button">
              <FaUserCog /> <span className="button-text">Conta</span>
            </Link>
          </>
        )}
        {isLoggedIn && isAdmin && (
          <>
            <Link to="/produtos" className="space-button">
              <FaHotel /> <span className="button-text">Configurar Produtos</span>
            </Link>
            <Link to="/camisas" className="space-button">
              <FaTshirt className="icon-camisa" />
              <span className="button-text">Configurar Camisas</span>
            </Link>
            <Link to="/artistas" className="space-button">
              <FaMusic /> <span className="button-text">Configurar Artistas</span>
            </Link>
            <Link to="/pedidos" className="space-button">
              <AiOutlineSchedule /> <span className="button-text">Ver pedidos</span>
            </Link>
            <Link to="/usuarios" className="space-button">
              <FaUser /> <span className="button-text">Usuários</span>
            </Link>
          </>
        )}
        {isLoggedIn ? (
          <button onClick={onLogout} className="logout-button">
            <FaSignOutAlt /> <span className="button-text">Sair</span>
          </button>
        ) : (
          <button onClick={onLogin} className="login-button">
            <FaSignInAlt /> <span className="button-text">Login</span>
          </button>
        )}
      </nav>
    </header>
  );
}

export default Header;
