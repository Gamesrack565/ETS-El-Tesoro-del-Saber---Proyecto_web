import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Search, Sparkles, ThumbsUp, ThumbsDown, 
  ChevronDown, PenTool, User, X 
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, 
  Tooltip, Legend 
} from 'recharts';
import api from '../../api/axiosConfig'; 
import './pagina_resenas.css';

const Pagina_Resenas = () => {
  // --- ESTADOS ---
  const [reseñas, setReseñas] = useState([]); // Lista que se muestra en pantalla
  const [loading, setLoading] = useState(true);
  const [filtro, setFiltro] = useState("");
  const [mostrarTodas, setMostrarTodas] = useState(false); // Switch para modo infinito
  const [visibleCount, setVisibleCount] = useState(5); // Cuántas reseñas renderizar en modo infinito
  const [statsData, setStatsData] = useState([]);
  const [user, setUser] = useState(null);
  
  const navigate = useNavigate();
  const observer = useRef(); // Referencia para el Intersection Observer

  // --- LÓGICA DE INFINITE SCROLL ---
  const lastElementRef = useCallback(node => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();

    observer.current = new IntersectionObserver(entries => {
      // Si el último elemento es visible y estamos en modo "Mostrar Todas", cargamos más
      if (entries[0].isIntersecting && mostrarTodas) {
        setVisibleCount(prev => prev + 5);
      }
    });

    if (node) observer.current.observe(node);
  }, [loading, mostrarTodas]);

  // --- EFECTOS INICIALES ---
  useEffect(() => {
    fetchRecientes(); // Carga inicial desde /stats/actividad-reciente
    fetchEstadisticas();
    checkUserSession();
  }, []);

  // --- FUNCIONES DE CARGA ---

  const checkUserSession = () => {
    const token = localStorage.getItem('token');
    if (token) {
      const savedName = localStorage.getItem('user_full_name') || "Estudiante";
      setUser({ name: savedName.split(' ')[0], fullName: savedName });
    }
  };

  // 1. Carga inicial: Solo las 5 más recientes
  const fetchRecientes = async () => {
    try {
      setLoading(true);
      const response = await api.get('/stats/actividad-reciente');
      setReseñas(response.data);
    } catch (error) {
      console.error("Error cargando recientes:", error);
    } finally {
      setLoading(false);
    }
  };

  // 2. Carga completa: Activa el modo infinito y trae todo de /reviews
  const fetchTodasLasResenas = async () => {
    try {
      setLoading(true);
      const response = await api.get('/reviews/resenas/');
      // Ordenamos por ID de mayor a menor (más nuevas arriba)
      const ordenadas = response.data.sort((a, b) => b.id - a.id);
      setReseñas(ordenadas);
      setMostrarTodas(true);
      setVisibleCount(10); // Iniciamos mostrando 10 al expandir
    } catch (error) {
      console.error("Error cargando todas las reseñas:", error);
    } finally {
      setLoading(false);
    }
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

  // --- INTERACCIONES ---

  const handleVoto = async (id, esUtil) => {
    if (!user) {
      alert("Debes iniciar sesión para votar.");
      return;
    }
    try {
      const response = await api.post('/reviews/votar', { resena_id: id, es_util: esUtil });
      setReseñas(prev => prev.map(res => 
        res.id === id ? { ...res, total_votos_utiles: response.data.total_utiles } : res
      ));
    } catch (error) { console.error(error); }
  };

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
    navigate('/login');
  };

  // --- FILTRADO Y VISIBILIDAD ---
  const coincidencias = reseñas.filter(r => {
    const busqueda = filtro.toLowerCase();
    // Validamos si profesor/materia vienen como objetos o strings según el endpoint
    const nombreProf = r.profesor?.nombre || r.profesor || "";
    const nombreMat = r.materia?.nombre || r.materia || "";
    const comentario = r.comentario || r.comentario_corto || "";

    return nombreProf.toLowerCase().includes(busqueda) || 
           nombreMat.toLowerCase().includes(busqueda) || 
           comentario.toLowerCase().includes(busqueda);
  });

  // Si estamos en modo infinito, cortamos el array. Si no, mostramos lo que haya.
  const reseñasAMostrar = mostrarTodas ? coincidencias.slice(0, visibleCount) : coincidencias;

  return (
    <div className="resenas-page-container">
      <div className="content-wrapper">
        
        {/* HEADER */}
        <header className="top-header-row">
          <h1 className="page-title">Reseñas</h1>
          <div className="user-status-widget">
            {user ? (
              <div className="logged-in-container">
                <span className="user-greeting-text">Hola, <strong>{user.name}</strong></span>
                <button className="btn-logout-red" onClick={handleLogout}>SALIR</button>
              </div>
            ) : (
              <Link to="/login" className="login-link-btn">Iniciar Sesión</Link>
            )}
          </div>
        </header>

        {/* BUSCADOR Y ACCIONES */}
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
                if (e.target.value !== "" && !mostrarTodas) fetchTodasLasResenas();
              }}
            />
            {filtro && <X className="close-icon" size={18} onClick={() => { setFiltro(""); setVisibleCount(10); }} />}
          </div>

          <button className="btn-add-review-compact" onClick={() => navigate(user ? '/agregar-resena' : '/login')}>
            <PenTool size={14} />
            <span>Escribir reseña</span>
          </button>
        </div>

        {/* CONTENIDO PRINCIPAL */}
        <main className="main-content">
          <div className="dos-columnas-layout">
            
            {/* COLUMNA IZQUIERDA: RESEÑAS */}
            <section className="columna-izquierda">
              <h2 className="section-header-title">
                {filtro ? `Resultados para "${filtro}"` : mostrarTodas ? "Todas las Reseñas" : "Reseñas Recientes"}
              </h2>
              
              <div className="reseñas-scroll-area">
                {loading && reseñas.length === 0 ? (
                  <div className="loading-state"><p>Cargando reseñas...</p></div>
                ) : reseñasAMostrar.length > 0 ? (
                  <>
                    {reseñasAMostrar.map((res, index) => {
                      const esUltimo = reseñasAMostrar.length === index + 1;
                      return (
                        <div 
                          key={res.id || index} 
                          className="reseña-card"
                          ref={esUltimo ? lastElementRef : null}
                        >
                          <div className="reseña-header">
                            <div className="reseña-info-top">
                              <span className="reseña-nombre">{res.profesor?.nombre || res.profesor}</span>
                              <span className="reseña-materia-tag">{res.materia?.nombre || res.materia}</span>
                            </div>
                            <span className="reseña-fecha">
                              {res.created_at ? new Date(res.created_at).toLocaleDateString() : "Reciente"}
                            </span>
                          </div>
                          
                          <div className="reseña-calif-bar">
                            <span className="star">⭐ {res.calificacion}/10</span>
                            {res.dificultad && <span className="difficulty">Dificultad: {res.dificultad}/10</span>}
                          </div>

                          <p className="reseña-comentario">{res.comentario || res.comentario_corto}</p>

                          <div className="voting-section">
                            <span className="vote-label">¿Es útil?</span>
                            <button className="vote-btn up" onClick={() => handleVoto(res.id, true)}>
                              <ThumbsUp size={16} /> <span>{res.total_votos_utiles || 0}</span>
                            </button>
                            <button className="vote-btn down" onClick={() => handleVoto(res.id, false)}>
                              <ThumbsDown size={16} />
                            </button>
                          </div>
                        </div>
                      );
                    })}

                    {/* BOTÓN "VER TODAS" (Solo se muestra en modo Recientes) */}
                    {!mostrarTodas && !filtro && reseñas.length >= 5 && (
                      <div className="ver-mas-container">
                        <button className="btn-ver-mas" onClick={fetchTodasLasResenas}>
                          Ver todas las reseñas <ChevronDown size={16} />
                        </button>
                      </div>
                    )}

                    {/* LOADER DE SCROLL INFINITO */}
                    {mostrarTodas && reseñasAMostrar.length < coincidencias.length && (
                      <div className="infinite-loader">Cargando más reseñas...</div>
                    )}
                  </>
                ) : (
                  <div className="no-results"><p>No se encontraron reseñas.</p></div>
                )}
              </div>
            </section>

            {/* COLUMNA DERECHA: STATS E IA */}
            <section className="columna-derecha">
              <div className="reputacion-section flex-graph-container">
                <h3 className="section-header-title">Estadísticas</h3>
                <div className="graph-wrapper">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={statsData} innerRadius="55%" outerRadius="75%" paddingAngle={5} dataKey="value">
                        {statsData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                      </Pie>
                      <Tooltip />
                      <Legend verticalAlign="bottom" height={36} iconSize={10} wrapperStyle={{ fontSize: '12px' }}/>
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="ia-section">
                <h3 className="ia-title-small">Pregúntale a la IA</h3>
                <div className="ia-input-wrapper">
                  <Sparkles className="ia-input-icon" size={18} />
                  <Link to="/menu" style={{ width: '100%', textDecoration: 'none' }}>
                    <input type="text" className="ia-input-bar" placeholder="Asistente Virtual..." readOnly />
                  </Link>
                </div>
              </div>
            </section>
          </div>
        </main>
      </div>
      
      {/* NAVEGACIÓN INFERIOR */}
      <div className="bottom-navigation-bar">
        <Link to="/portal" className="nav-link"><button className="nav-pill-button">Portal</button></Link>  
        <Link to="/horarios" className="nav-link"><button className="nav-pill-button">Horarios</button></Link>
        <Link to="/menu" className="nav-link"><button className="nav-pill-button">Asistente</button></Link>          
      </div>
    </div>
  );
};

export default Pagina_Resenas;