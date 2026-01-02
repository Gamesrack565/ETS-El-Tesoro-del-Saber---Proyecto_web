import React, { useState, useEffect } from 'react';
import { Search, Sparkles, ThumbsUp, ThumbsDown, ChevronDown, ChevronUp, PenTool, User } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import api from '../../api/axiosConfig'; 
import './pagina_resenas.css';

const Pagina_Resenas = () => {
  const [reseñas, setReseñas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtro, setFiltro] = useState("");
  const [mostrarTodas, setMostrarTodas] = useState(false);
  const [statsData, setStatsData] = useState([]);
  const [user, setUser] = useState(null);
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchReseñas();
    fetchEstadisticas();
    checkUserSession();
  }, []);

  const checkUserSession = async () => {
      const token = localStorage.getItem('token');
      if (token) {
          try {
              const savedName = localStorage.getItem('user_full_name') || "Estudiante";
              // Tomamos solo el primer nombre para que se vea mejor (opcional)
              const firstName = savedName.split(' ')[0]; 
              setUser({ name: firstName, fullName: savedName });
          } catch (e) { setUser(null); }
      }
  };

  const handleLogout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('user_full_name');
      setUser(null);
      navigate('/login');
  };

  const fetchReseñas = async () => {
    try {
      const response = await api.get('/reviews/resenas/');
      const ordenadas = response.data.sort((a, b) => b.id - a.id);
      setReseñas(ordenadas);
    } catch (error) { console.error(error); } 
    finally { setLoading(false); }
  };

  const fetchEstadisticas = async () => {
      try {
          const response = await api.get('/stats/general');
          const data = response.data; 
          setStatsData([
              { name: 'Usuarios', value: data.usuarios, color: '#4B6CB7' },
              { name: 'Reseñas', value: data.resenas, color: '#72EDF2' },
              { name: 'Recursos', value: data.recursos, color: '#2E89BA' },
              { name: 'Profesores', value: data.profesores, color: '#51B5E0' },
          ]);
      } catch (error) { console.error(error); }
  };

  const handleVoto = async (id, esUtil) => {
    if (!user) {
        alert("Necesitas iniciar sesión para votar.");
        return;
    }
    try {
        const response = await api.post('/reviews/votar', { resena_id: id, es_util: esUtil });
        setReseñas(prev => prev.map(res => {
            if (res.id === id) {
                return {
                    ...res,
                    total_votos_utiles: response.data.total_utiles !== undefined 
                        ? response.data.total_utiles 
                        : (res.total_votos_utiles || 0) + 1
                };
            }
            return res;
        }));
    } catch (error) { console.error(error); }
  };

  const handleCrearResena = () => {
      if (!user) {
          alert("Debes iniciar sesión para escribir una reseña.");
          navigate('/login');
      } else {
          navigate('/agregar-resena');
      }
  };


  const coincidencias = reseñas.filter(r => {
    const busqueda = filtro.toLowerCase();
    return (r.profesor?.nombre?.toLowerCase() || "").includes(busqueda) || 
           (r.materia?.nombre?.toLowerCase() || "").includes(busqueda) || 
           (r.comentario?.toLowerCase() || "").includes(busqueda);
  });

  let reseñasVisibles = coincidencias;
  let tituloSeccion = "";

  if (filtro) {
      tituloSeccion = `Resultados: "${filtro}"`;
  } else {
      if (mostrarTodas) {
          reseñasVisibles = reseñas;
          tituloSeccion = "Todas las Reseñas";
      } else {
          reseñasVisibles = reseñas.slice(0, 5); 
          tituloSeccion = "Reseñas Recientes";
      }
  }

  return (
    <div className="resenas-page-container">
      <div className="content-wrapper">
        
        {/* --- HEADER: Título y Usuario Estilo Home --- */}
        <header className="top-header-row">
            <h1 className="page-title">Reseñas</h1>
            
            <div className="user-status-widget">
                {user ? (
                    <div className="logged-in-container">
                        <span className="user-greeting-text">
                            Hola, <strong>{user.name}</strong>
                        </span>
                        <button className="btn-logout-red" onClick={handleLogout}>
                            SALIR
                        </button>
                    </div>
                ) : (
                    <Link to="/login" className="login-link-btn">
                        <User size={16} style={{marginRight: 5}}/> Iniciar Sesión
                    </Link>
                )}
            </div>
        </header>

        {/* --- ACCIONES: Buscador y Botón Compacto --- */}
        <div className="actions-row">
            <div className="search-bar-container">
                <Search className="search-icon" size={18} />
                <input 
                    type="text" 
                    className="search-input" 
                    placeholder="Buscar profesor o materia..." 
                    value={filtro}
                    onChange={(e) => {
                        setFiltro(e.target.value);
                        if(!mostrarTodas) setMostrarTodas(true); 
                    }}
                />
                {filtro && <span className="close-icon" onClick={() => {
                    setFiltro('');
                    setMostrarTodas(false);
                }}>✖</span>}
            </div>

            <button className="btn-add-review-compact" onClick={handleCrearResena}>
                <PenTool size={14} />
                <span>Escribe algo de tu profesor</span>
            </button>
        </div>

        <main className="main-content">
          <div className="dos-columnas-layout">
            
            <section className="columna-izquierda">
              <h2 className="section-header-title">{tituloSeccion}</h2>
              
              <div className="reseñas-scroll-area">
                {loading ? (
                    <div className="loading-state"><p>Cargando reseñas...</p></div>
                ) : reseñasVisibles.length > 0 ? (
                    <>
                      {reseñasVisibles.map((reseña) => (
                          <div key={reseña.id} className="reseña-card">
                          <div className="reseña-header">
                              <div className="reseña-info-top">
                                  <span className="reseña-nombre">
                                      {reseña.profesor ? reseña.profesor.nombre : "Desconocido"}
                                  </span>
                                  <span className="reseña-materia-tag">
                                      {reseña.materia ? reseña.materia.nombre : "General"}
                                  </span>
                              </div>
                              <span className="reseña-fecha">
                                  {reseña.created_at 
                                      ? new Date(reseña.created_at).toLocaleDateString() 
                                      : "Reciente"}
                              </span>
                          </div>
                          
                          <div className="reseña-calif-bar">
                              <span className="star">⭐ {reseña.calificacion}/10</span>
                              <span className="difficulty">Dificultad: {reseña.dificultad}/10</span>
                          </div>

                          <p className="reseña-comentario">{reseña.comentario}</p>

                          <div className="voting-section">
                              <span className="vote-label">¿Es útil?</span>
                              <button className="vote-btn up" onClick={() => handleVoto(reseña.id, true)}>
                                  <ThumbsUp size={16} /> <span>{reseña.total_votos_utiles || 0}</span>
                              </button>
                              <button className="vote-btn down" onClick={() => handleVoto(reseña.id, false)}>
                                  <ThumbsDown size={16} />
                              </button>
                          </div>
                          </div>
                      ))}

                      {!filtro && reseñas.length > 5 && (
                          <div className="ver-mas-container">
                              <button 
                                  className="btn-ver-mas"
                                  onClick={() => setMostrarTodas(!mostrarTodas)}
                              >
                                  {mostrarTodas ? (
                                      <>Ver recientes <ChevronUp size={16} /></>
                                  ) : (
                                      <>Ver todas ({reseñas.length}) <ChevronDown size={16} /></>
                                  )}
                              </button>
                          </div>
                      )}
                    </>
                ) : (
                    <div className="no-results">
                        <p>No se encontraron reseñas.</p>
                    </div>
                )}
              </div>
            </section>

            <section className="columna-derecha">
              <div className="reputacion-section flex-graph-container">
                <h3 className="section-header-title">Estadísticas Generales</h3>
                <div className="graph-wrapper">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={statsData}
                        innerRadius="55%"
                        outerRadius="75%"
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {statsData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend verticalAlign="bottom" height={36} iconSize={10} wrapperStyle={{ fontSize: '12px' }}/>
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="ia-section">
                <h3 className="ia-title-small">¿Alguna duda? Pregúntale a la IA</h3>
                <div className="ia-input-wrapper">
                  <Sparkles className="ia-input-icon" size={18} />
                  <Link to="/menu" style={{ width: '100%', textDecoration: 'none' }}>
                      <input
                        type="text"
                        className="ia-input-bar"
                        placeholder="Asistente Virtual..."
                        readOnly 
                        style={{ cursor: 'pointer' }}
                      />
                  </Link>
                </div>
              </div>
            </section>
          </div>
        </main>
      </div>
      
      <div className="bottom-navigation-bar">
        <Link to="/portal" className="nav-link">
          <button className="nav-pill-button">Portal Estudiantil</button>
        </Link>  
        <Link to="/horarios" className="nav-link">
          <button className="nav-pill-button">Horarios y Calendarios</button>
        </Link>
        <Link to="/menu" className="nav-link">
          <button className="nav-pill-button">Asistente Virtual</button>
        </Link>          
      </div>
    </div>
  );
};

export default Pagina_Resenas;