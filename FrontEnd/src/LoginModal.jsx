import React, { useState } from 'react';
import { FaSignInAlt, FaUserPlus, FaTimes, FaEye, FaEyeSlash } from 'react-icons/fa';
import { toast } from 'react-toastify';
import './LoginModal.css';

function LoginModal({ isOpen, onClose, onLoginSuccess }) {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    username: ''
  });
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const toggleMode = () => {
    setIsRegisterMode(!isRegisterMode);
    setFormData({ email: '', password: '', confirmPassword: '', username: '' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    if (isRegisterMode) {
      // Lógica de cadastro
      try {
        // Validações
        if (formData.password !== formData.confirmPassword) {
          toast.error('As senhas não coincidem.');
          setIsLoading(false);
          return;
        }

        if (formData.password.length < 6) {
          toast.error('A senha deve ter pelo menos 6 caracteres.');
          setIsLoading(false);
          return;
        }

        const response = await fetch(`${apiUrl}/auth/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
            usuario: formData.username
          }),
        });

        const data = await response.json();

        if (response.ok) {
          toast.success('Cadastro realizado com sucesso! Verifique seu email para confirmar a conta.');
          
          // Limpar campos e voltar para modo login
          setFormData({ email: '', password: '', confirmPassword: '', username: '' });
          setIsRegisterMode(false);
        } else {
          toast.error(data.detail || 'Erro ao fazer cadastro');
        }
      } catch (error) {
        console.error('Erro no cadastro:', error);
        toast.error('Erro de conexão. Tente novamente.');
      } finally {
        setIsLoading(false);
      }
    } else {
      // Lógica de login (existente)
      try {
      const response = await fetch(`${apiUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user_id', data.user.id);
        localStorage.setItem('email', data.user.email);
        localStorage.setItem('usuario', data.user.usuario || '');
        localStorage.setItem('is_admin', data.user.is_admin);
        localStorage.setItem('username', formData.email);
        toast.success('Login realizado com sucesso!');
        
        // Chamar callback de sucesso se fornecido
        if (onLoginSuccess) {
          onLoginSuccess();
        } else {
          onClose();
        }
        
        // Resetar formulário
        setFormData({ email: '', password: '', confirmPassword: '', username: '' });
      } else {
        toast.error(data.detail || 'Erro ao fazer login');
      }
    } catch (error) {
      console.error('Erro no login:', error);
      toast.error('Erro de conexão. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <FaTimes />
        </button>
        
        <div className="modal-header">
          <h2>{isRegisterMode ? 'Cadastrar Nova Conta' : 'Login Necessário'}</h2>
        </div>
        
        <div className="modal-body">
          <p>
            {isRegisterMode 
              ? 'Preencha os dados abaixo para criar sua conta.'
              : 'É necessário estar logado para adicionar produtos ao carrinho.'
            }
          </p>
          
          <form onSubmit={handleSubmit} className="login-form">
            {isRegisterMode && (
              <div className="form-group">
                <label htmlFor="username">Nome de usuário:</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  required
                  placeholder="Digite seu nome de usuário"
                />
              </div>
            )}

            <div className="form-group">
              <label htmlFor="email">Email:</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                placeholder="Digite seu email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Senha:</label>
              <div className="password-input-container">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  placeholder="Digite sua senha"
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
            </div>

            {isRegisterMode && (
              <div className="form-group">
                <label htmlFor="confirmPassword">Confirmar Senha:</label>
                <div className="password-input-container">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    id="confirmPassword"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    required
                    placeholder="Confirme sua senha"
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
              </div>
            )}

            <div className="modal-actions">
              <button 
                type="submit" 
                className="btn-login-modal"
                disabled={isLoading}
              >
                {isRegisterMode ? <FaUserPlus /> : <FaSignInAlt />}
                {isLoading 
                  ? (isRegisterMode ? 'Cadastrando...' : 'Entrando...') 
                  : (isRegisterMode ? 'Cadastrar' : 'Fazer Login')
                }
              </button>
              
              <button 
                type="button" 
                className="btn-register-modal"
                onClick={toggleMode}
              >
                {isRegisterMode ? <FaSignInAlt /> : <FaUserPlus />}
                {isRegisterMode ? 'Já tem conta? Faça login' : 'Não tem conta? Cadastre-se'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default LoginModal;
