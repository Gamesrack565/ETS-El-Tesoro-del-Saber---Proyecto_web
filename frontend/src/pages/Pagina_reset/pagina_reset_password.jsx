import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../../api/axiosConfig'; 
import './pagina_reset_password.css'; // Usaremos un CSS consistente

function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const [token, setToken] = useState('');
  const [passwords, setPasswords] = useState({ new: '', confirm: '' });
  const [status, setStatus] = useState({ loading: false, error: '', success: '' });

  useEffect(() => {
    // Extraer el token de la URL (ej: ?token=eyJhbGci...)
    const tokenFromUrl = searchParams.get('token');
    if (tokenFromUrl) {
      setToken(tokenFromUrl);
    } else {
      setStatus({ ...status, error: 'Enlace inválido o incompleto.' });
    }
  }, [searchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ loading: true, error: '', success: '' });

    if (passwords.new !== passwords.confirm) {
      setStatus({ loading: false, error: 'Las contraseñas no coinciden.', success: '' });
      return;
    }

    if (passwords.new.length < 8) {
      setStatus({ loading: false, error: 'Mínimo 8 caracteres.', success: '' });
      return;
    }

    try {
      // Ajusta '/users' si tu prefijo en main.py es diferente
      await api.post('/users/reset-password', {
        token: token,
        new_password: passwords.new
      });

      setStatus({ loading: false, error: '', success: '¡Contraseña restablecida con éxito!' });
      
      // Redirigir al login después de 2 segundos
      setTimeout(() => navigate('/login'), 2000);

    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'El enlace ha expirado o es inválido.';
      setStatus({ loading: false, error: errorMsg, success: '' });
    }
  };

  return (
    <div className="auth-container">
      <div className="user-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
        </svg>
      </div>

      <h2 className="auth-title">Nueva Contraseña</h2>
      <p className="auth-subtitle">Ingresa tu nueva clave de acceso</p>

      <form className="auth-form" onSubmit={handleSubmit}>
        
        {status.error && <div className="alert-box error">{status.error}</div>}
        {status.success && <div className="alert-box success">{status.success}</div>}

        <label htmlFor="new_pass">Nueva Contraseña</label>
        <input 
          type="password" 
          id="new_pass"
          placeholder="********" 
          value={passwords.new}
          onChange={(e) => setPasswords({...passwords, new: e.target.value})}
          required
          disabled={!token || status.success}
        />

        <label htmlFor="confirm_pass">Confirmar Contraseña</label>
        <input 
          type="password" 
          id="confirm_pass"
          placeholder="********" 
          value={passwords.confirm}
          onChange={(e) => setPasswords({...passwords, confirm: e.target.value})}
          required
          disabled={!token || status.success}
        />

        <button 
          type="submit" 
          className="btn btn-primary" 
          disabled={status.loading || !token || status.success}
        >
          {status.loading ? 'Guardando...' : 'Cambiar Contraseña'}
        </button>

      </form>
    </div>
  );
}

export default ResetPasswordPage;