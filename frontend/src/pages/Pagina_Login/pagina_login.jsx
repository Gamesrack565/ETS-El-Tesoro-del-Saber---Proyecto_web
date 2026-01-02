import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../../api/axiosConfig'; 
import './pagina_login.css'; 

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  
  // Estados para Recuperación de Contraseña
  const [showResetModal, setShowResetModal] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [resetStatus, setResetStatus] = useState({ loading: false, msg: '', error: '' });

  const navigate = useNavigate(); 

  // --- LOGIN ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);

    try {
      const response = await api.post('/users/login', params);
      localStorage.setItem('token', response.data.access_token);
      
      if (response.data.full_name) {
          localStorage.setItem('user_full_name', response.data.full_name);
          finalizarLogin();
      } else {
          try {
              const userResponse = await api.get('/users/me', {
                  headers: { Authorization: `Bearer ${response.data.access_token}` }
              });
              localStorage.setItem('user_full_name', userResponse.data.full_name);
          } catch (error) {
              localStorage.setItem('user_full_name', "Estudiante");
          }
          finalizarLogin();
      }

    } catch (err) {
      if (err.response) {
        if (err.response.status === 401) setError("Correo o contraseña incorrectos.");
        else setError(err.response.data.detail || "Error al iniciar sesión.");
      } else {
        setError("No se pudo conectar con el servidor.");
      }
    }
  };

  const finalizarLogin = () => {
      alert("¡Bienvenido al Tesoro del Saber!");
      navigate('/'); 
  };

  // --- RECUPERAR CONTRASEÑA ---
  const handleRequestReset = async (e) => {
      e.preventDefault();
      setResetStatus({ loading: true, msg: '', error: '' });

      if (!resetEmail) {
          setResetStatus({ loading: false, msg: '', error: 'Ingresa tu correo.' });
          return;
      }

      try {
          // Ajusta '/users' si tu prefijo es diferente en main.py
          await api.post('/users/request-password-reset', { email: resetEmail });
          setResetStatus({ 
              loading: false, 
              msg: 'Si el correo existe, recibirás instrucciones pronto.', 
              error: '' 
          });
          setTimeout(() => {
              setShowResetModal(false);
              setResetStatus({ loading: false, msg: '', error: '' });
              setResetEmail('');
          }, 3000);
      } catch (err) {
          setResetStatus({ 
              loading: false, 
              msg: '', 
              error: 'Error al enviar la solicitud.' 
          });
      }
  };

  return (
    <div className='auth-container'>
      <div className="user-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </svg>
      </div>

      {!showResetModal ? (
          /* --- FORMULARIO LOGIN --- */
          <form className='auth-form' onSubmit={handleSubmit}>
            {error && <div className="error-alert">{error}</div>}

            <label htmlFor='correo'>Correo</label>
            <input 
              type='email' id='correo' placeholder='correo@dominio.com' 
              value={email} onChange={(e) => setEmail(e.target.value)} required
            />
            
            <label htmlFor='password'>Contraseña</label>
            <input 
              type='password' id='password' placeholder='Ingrese la contraseña' 
              value={password} onChange={(e) => setPassword(e.target.value)} required
            />
            
            <button type='submit' className='btn btn-primary'>Entrar</button>

            {/* Enlace para recuperar contraseña */}
            <div className="forgot-password-link">
                <button type="button" onClick={() => setShowResetModal(true)} className="btn-text">
                    ¿Olvidaste tu contraseña?
                </button>
            </div>

            <div className="register-link-container">
                <span>¿No tienes cuenta? </span>
                <Link to="/registro" className="register-link">Regístrate aquí</Link>
            </div>
          </form>
      ) : (
          /* --- MODAL RECUPERACIÓN (INLINE) --- */
          <div className="reset-password-container">
              <h3>Recuperar Contraseña</h3>
              <p>Ingresa tu correo y te enviaremos un enlace mágico.</p>
              
              <form onSubmit={handleRequestReset} className="auth-form">
                  <input 
                      type="email" 
                      placeholder="tucorreo@ipn.mx" 
                      value={resetEmail}
                      onChange={(e) => setResetEmail(e.target.value)}
                  />
                  
                  {resetStatus.msg && <div className="success-msg">{resetStatus.msg}</div>}
                  {resetStatus.error && <div className="error-alert">{resetStatus.error}</div>}

                  <button type="submit" className="btn btn-primary" disabled={resetStatus.loading}>
                      {resetStatus.loading ? 'Enviando...' : 'Enviar Enlace'}
                  </button>
                  
                  <button 
                      type="button" 
                      className="btn btn-secondary" 
                      onClick={() => setShowResetModal(false)}
                  >
                      Volver al Login
                  </button>
              </form>
          </div>
      )}
    </div>
  );
}

export default LoginPage;