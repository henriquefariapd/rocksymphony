import React from 'react';
import { Link } from 'react-router-dom';
import { FaSignInAlt, FaUserPlus, FaTimes } from 'react-icons/fa';
import './LoginModal.css';

function LoginModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <FaTimes />
        </button>
        
        <div className="modal-header">
          <h2>Login Necessário</h2>
        </div>
        
        <div className="modal-body">
          <p>É necessário estar logado para adicionar produtos ao carrinho.</p>
          
          <div className="modal-actions">
            <Link to="/login" className="btn-login-modal">
              <FaSignInAlt />
              Fazer Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginModal;
