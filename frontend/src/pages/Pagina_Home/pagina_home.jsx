import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axiosConfig'; // Importamos la conexión
import './pagina_home.css';

function HomePage() {
  const [user, setUser] = useState(null);
  const [topProfesores, setTopProfesores] = useState([]); // Estado para el ranking

  // Al cargar la página
  useEffect(() => {
    const initData = async () => {
      // 1. Verificar Sesión
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const response = await api.get('/users/me');
          setUser(response.data);
        } catch (error) {
          console.error("Sesión expirada");
          localStorage.removeItem('token');
        }
      }

            // 2. Cargar Top Profesores (Público)
      try {
        const resRanking = await api.get('/stats/top-profesores?limit=4');
        
        // VERIFICACIÓN DE SEGURIDAD:
        // Si lo que llega ES un array, lo usamos.
        // Si NO es un array (es null, error, objeto, etc.), usamos una lista vacía [].
        if (Array.isArray(resRanking.data)) {
            setTopProfesores(resRanking.data);
        } else {
            console.warn("El backend no devolvió una lista, usando lista vacía.");
            setTopProfesores([]); 
        }

      } catch (error) {
        console.error("Error cargando top profesores:", error);
        setTopProfesores([]); // En caso de error, también aseguramos que sea lista vacía
      }
    };

    initData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    window.location.reload();
  };

  return (
    <div className="homepage-container">
      
      {/* --- Encabezado / Navbar --- */}
      <header className="home-header">
        <div className="logo-container">
          <h1 className="logo-title">ETS</h1>
          <span className="logo-subtitle">El Tesoro del Saber</span>
        </div>
        
        <nav className="main-nav">
          <Link to="/menu" className="btn-menu-cuadrado">
              Menú Principal
          </Link>
          <Link to="/portal">Portal Estudiantil</Link>
          <Link to="/resenas">Reseñas de Profesores</Link>
          <Link to="/horarios">Horarios y Calendarios</Link>
        </nav>
        
        <div className="auth-links">
          {user ? (
            <div className="user-info-header">
                <span className="welcome-text">
                    Hola, <strong>{user.full_name.split(' ')[0]}</strong>
                </span>
                <button onClick={handleLogout} className="btn-logout">
                    Salir
                </button>
            </div>
          ) : (
            <>
                <Link to="/login" className="btn-link">Iniciar Sesión</Link>
                <Link to="/registro" className="btn-link btn-link-primary">Registrarse</Link>
            </>
          )}
        </div>
      </header>

      <main>
        {/* --- Sección Top de Profesores (DINÁMICA) --- */}
        <section className="top-profesores-section">
          <h2>🏆 Top Profesores ESCOM:</h2>
          
          <div className="professors-list">
            {topProfesores.length > 0 ? (
                topProfesores.map((prof, index) => (
                    <div key={index} className="profesor-card">
                        <div className="profesor-info">
                            {/* Nombre del Profe */}
                            <h3>{prof.nombre}</h3> 
                            
                            {/* Total de reseñas */}
                            <p className="resenas-count">{prof.total_resenas} reseñas registradas</p>
                            
                            {/* Fragmento del comentario (Nuevo) */}
                            {prof.ultimo_comentario && (
                                <div className="review-snippet">
                                    "{prof.ultimo_comentario}"
                                </div>
                            )}
                        </div>
                        
                        <div className="profesor-rating">
                            {/* Badge de calificación */}
                            <div className="score-badge">
                                ⭐ {prof.valor}/10
                            </div>
                        </div>
                    </div>
                ))
            ) : (
                <p style={{color: '#666', fontStyle: 'italic', textAlign: 'center'}}>Cargando ranking...</p>
            )}
          </div>
        </section>

        {/* --- Sección de Misión, Cita y Visión --- */}
        <section className="mision-vision-container">
          <div className="mv-row">
            <div className="mv-card">
            <h2>Misión</h2>
            <p>Proveer a la comunidad estudiantil de la
               ESCOM una plataforma digital
               centralizada y colaborativa que facilite
               la toma de decisiones académicas,
               fomente el intercambio de
               conocimiento y optimice la gestión de
               recursos educativos.</p>
          </div>
          
          <div className="mv-card">
            <h2>Visión</h2>
            <p>Ser la herramienta digital indispensable
               y de referencia para la vida académica
               de todos los estudiantes de la ESCOM,
               reconocida por su fiabilidad, utilidad y
               por fomentar una comunidad
               estudiantil más conectada y exitosa.</p>
            </div>
          </div>

          <div className="quote-container">
            <blockquote>"Ninguno de nosotros es tan bueno como todos nosotros juntos."</blockquote>
            <cite>- Ray Kroc</cite>
          </div>

        </section>

        <section className="features">
          <div className="feature-card">
            <h3>Que tu voz sea escuchada</h3>
            <h4>Comparte tu experiencia</h4>
            <p>Si tienes alguna experiencia que quieras compartir sobre un profesor, este es el sitio adecuado.</p>
          </div>

          <div className="feature-card">
            <h3>Apoyo a la comunidad</h3>
            <div className="spacer"></div>
            <p>Puedes consultar el portal estudiantil donde encontrarás apuntes, exámenes y prácticas que pueden ayudarte.</p>
          </div>

          <div className="feature-card">
            <h3>Mantente al tanto</h3>
            <div className="spacer"></div>
            <p>Contamos con calendarios y datos oficiales para que construyas tu horario. Te acompañamos para que tomes la mejor decisión.</p>
          </div>
        </section>
      </main>

      {/* --- Pie de página --- */}
      <footer className="home-footer">
        <p>Contáctanos: correo@dominio.com</p>
        <p>55 1122 3344</p>
      </footer>

    </div>
  );
}

export default HomePage;