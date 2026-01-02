import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig'; // Asegúrate de importar tu cliente axios
import './pagina_asistente.css';

const Pagina_Asistente = () => {
  const [user, setUser] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null); // Respuesta del bot
  const [loading, setLoading] = useState(false); // Estado de carga
  
  const navigate = useNavigate();

  // 1. Verificar sesión y obtener datos del usuario
  useEffect(() => {
    const token = localStorage.getItem('token');
    
    if (token) {
        const savedName = localStorage.getItem('user_full_name') || "Estudiante";
        // Intentamos obtener el ID del usuario del localStorage si lo guardaste en el login
        // Si no, tendremos que hacer un fetch a /users/me. 
        // Por ahora asumo que guardaste el ID o haremos un fetch rápido.
        obtenerUsuarioReal(token, savedName);
    } else {
        setUser(null);
    }
  }, []);

  const obtenerUsuarioReal = async (token, name) => {
      try {
          // Hacemos fetch a /users/me para obtener el ID real
          const response = await api.get('/users/me', {
             headers: { Authorization: `Bearer ${token}` }
          });
          setUser({ 
              name: response.data.full_name, 
              id: response.data.id 
          });
      } catch (error) {
          console.error("Error obteniendo usuario", error);
          // Fallback con datos locales si falla la red
          setUser({ name: name, id: null }); 
      }
  };

  const handleLogout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('user_full_name');
      setUser(null);
      navigate('/login');
  };

  // 2. FUNCIÓN PARA ENVIAR AL CHATBOT
  const handleSend = async () => {
      if (!question.trim()) return;
      if (!user) return; // Seguridad extra

      setLoading(true);
      setAnswer(null); // Limpiar respuesta anterior mientras piensa

      try {
          // Estructura que espera tu esquema PreguntaChat (Pydantic)
          const payload = {
              texto: question,
              user_id: user.id || 0, // 0 si no se pudo recuperar ID
              materia_id: 0 // 0 para que la IA detecte la materia automáticamente
          };

          const response = await api.post('/bot/preguntar', payload);
          
          // Guardar la respuesta
          setAnswer(response.data.respuesta);

      } catch (error) {
          console.error("Error del bot:", error);
          setAnswer("Lo siento, tuve un problema al conectar con mis servidores. Intenta de nuevo.");
      } finally {
          setLoading(false);
          setQuestion(""); // Limpiar campo
      }
  };

  return (
    <div className="asistente-page-container">
      
      {/* Encabezado */}
      <header className="asistente-header">
        <h1>Asistente Virtual</h1>
        
        <div className="header-user-area">
            {user ? (
                <div className="user-logged-info">
                    <span className="user-greeting">👋 Hola, {user.name}</span>
                    <button className="btn-logout-mini" onClick={handleLogout}>Salir</button>
                </div>
            ) : (
                <Link to="/login" className="btn-login-header">
                    Iniciar Sesión ➝
                </Link>
            )}
        </div>
      </header>

      {/* Contenido Principal */}
      <main className="asistente-main-content">
        <div className="conversation-wrapper">
            
            {/* 1. SECCIÓN DE RESPUESTA (Arriba) */}
            <section className="answer-section">
                <h2 className="section-label">Respuesta del Asistente:</h2>
                <div className="answer-bar">
                    {loading ? (
                        <p className="typing-indicator">Pensando... 🧠</p>
                    ) : answer ? (
                        // Usamos white-space: pre-wrap en CSS para respetar saltos de línea
                        <p className="bot-response-text">{answer}</p>
                    ) : (
                        <p className="placeholder-text">
                            Aquí aparecerá la respuesta a tus dudas escolares...
                        </p>
                    )}
                </div>
            </section>

            {/* 2. SECCIÓN DE PREGUNTA (Abajo) */}
            <section className="question-section">
                <h2 className="section-label">Tu Pregunta:</h2>

                {!user && (
                    <div className="auth-warning-message">
                        🚫 ESTO SOLO LO PUEDEN USAR LAS PERSONAS QUE TENGAN UNA CUENTA
                    </div>
                )}

                <div className={`question-box-container ${!user ? 'disabled-box' : ''}`}>
                    <textarea
                        className="question-textarea-borderless"
                        placeholder={user ? "Escribe tu duda aquí..." : "Debes iniciar sesión para escribir..."}
                        disabled={!user || loading}
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSend();
                            }
                        }}
                    ></textarea>

                    <div className="question-box-footer">
                        <button 
                            className='send-button-integrated'
                            disabled={!user || loading || !question.trim()}
                            onClick={handleSend}
                        >
                            {loading ? "Enviando..." : "Enviar Pregunta"}
                        </button>
                    </div>
                </div>
            </section>

        </div>
      </main>

      {/* Barra de Navegacion */}
      <div className="bottom-navigation-bar">
        <Link to="/portal" className="nav-link">
          <button className="nav-pill-button">Portal Estudiantil</button>
        </Link>
        
        <Link to="/horarios" className="nav-link">
          <button className="nav-pill-button">Horarios y Calendarios</button>
        </Link>
        
        <button className="nav-pill-button active">Asistente Virtual</button>
      </div>
    </div>
  );
};

export default Pagina_Asistente;