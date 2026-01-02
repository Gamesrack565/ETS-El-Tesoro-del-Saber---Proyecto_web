import React, { useState, useEffect, useRef } from 'react';
import { Save, ChevronLeft, Star, BarChart, BookOpen, User, Search, Plus, LogOut } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig'; 
import './agregar_resena.css';

const AgregarResena = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  
  // Datos del catálogo (Vienen de la API)
  const [profesores, setProfesores] = useState([]);
  const [materias, setMaterias] = useState([]); // Nueva lista para materias
  
  // Estados para el Autocomplete del Profesor
  const [busquedaProfe, setBusquedaProfe] = useState("");
  const [profesorSeleccionado, setProfesorSeleccionado] = useState(null);
  const [mostrarSugerencias, setMostrarSugerencias] = useState(false);
  const wrapperRef = useRef(null);

  // Estado Usuario
  const [user, setUser] = useState(null);

  const [formData, setFormData] = useState({
    comentario: "",
    calificacion: 5,
    dificultad: 5,
    materia_nombre: "" // Esto ahora vendrá del select
  });

  // Cargar datos iniciales (Profes y Materias)
  useEffect(() => {
    const cargarCatalogos = async () => {
        try {
            const [resProfes, resMaterias] = await Promise.all([
                api.get('/catalogos/profesores/'),
                api.get('/catalogos/materias/')
            ]);
            setProfesores(resProfes.data);
            setMaterias(resMaterias.data);
        } catch (error) {
            console.error("Error cargando catálogos:", error);
        }
    };
    
    checkUserSession();
    cargarCatalogos();
  }, []);

  const checkUserSession = () => {
      const token = localStorage.getItem('token');
      if (token) {
          const savedName = localStorage.getItem('user_full_name') || "Estudiante";
          setUser({ name: savedName.split(' ')[0] });
      } else {
          alert("Debes iniciar sesión.");
          navigate('/login');
      }
  };

  const handleLogout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('user_full_name');
      navigate('/login');
  };

  // Manejo de clicks fuera del autocomplete
  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setMostrarSugerencias(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [wrapperRef]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({ ...prevState, [name]: value }));
  };

  const handleSliderChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({ ...prevState, [name]: parseInt(value) }));
  };

  // --- LÓGICA AUTOCOMPLETE PROFESOR ---
  const profesoresFiltrados = profesores.filter(p => 
    p.nombre.toLowerCase().includes(busquedaProfe.toLowerCase())
  );

  const seleccionarProfesor = (profe) => {
      setProfesorSeleccionado(profe);
      setBusquedaProfe(profe.nombre);
      setMostrarSugerencias(false);
  };

  const usarNuevoProfesor = () => {
      const nuevo = { id: 0, nombre: busquedaProfe, esNuevo: true };
      setProfesorSeleccionado(nuevo);
      setMostrarSugerencias(false);
  };
  // ------------------------------------

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!profesorSeleccionado || !formData.materia_nombre || !formData.comentario) {
        alert("Por favor completa todos los campos.");
        return;
    }

    setLoading(true);

    const payload = {
        comentario: formData.comentario,
        calificacion: parseInt(formData.calificacion),
        dificultad: parseInt(formData.dificultad),
        materia_nombre: formData.materia_nombre,
        
        // 0 si es nuevo, ID real si existe
        profesor_id: profesorSeleccionado.id, 
        // Solo enviamos nombre si es nuevo
        profesor_nombre_nuevo: profesorSeleccionado.esNuevo ? profesorSeleccionado.nombre : null 
    };

    try {
      await api.post('/reviews/resenas/', payload);
      alert("¡Reseña publicada con éxito!");
      navigate('/resenas');
    } catch (error) {
      console.error("Error:", error);
      alert("Error al publicar. Revisa que no uses palabras prohibidas.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="resenas-page-container no-scroll">
      
      <header className="form-header-grid">
         <div className="header-left">
            <button onClick={() => navigate('/resenas')} className="btn-back">
                <ChevronLeft size={20}/> <span className="back-text">Volver</span>
            </button>
         </div>
         <div className="header-center">
            <h1 className="page-title">Nueva Reseña</h1>
         </div>
         <div className="header-right">
            {user && (
                <div className="logged-in-container-small">
                    <span className="user-greeting-small">Hola, <strong>{user.name}</strong></span>
                    <button className="btn-logout-red-small" onClick={handleLogout}>SALIR</button>
                </div>
            )}
         </div>
      </header>

      <main className="form-content-wrapper">
        <div className="form-card compact-card">
            <div className="text-center mb-4">
                <h2 className="form-title">Cuéntanos tu experiencia</h2>
                <p className="form-subtitle">Tu opinión ayuda a otros estudiantes.</p>
            </div>

            <form onSubmit={handleSubmit} className="compact-form">
                
                <div className="form-row">
                    {/* BUSCADOR DE PROFESOR (Con opción de crear) */}
                    <div className="input-group half-width" ref={wrapperRef}>
                        <label className="input-label"><User size={16}/> Profesor</label>
                        <div className="autocomplete-container">
                            <input 
                                type="text"
                                className={`custom-input ${profesorSeleccionado?.esNuevo ? 'input-new-tag' : ''}`}
                                placeholder="Busca o agrega nuevo..."
                                value={busquedaProfe}
                                onChange={(e) => {
                                    setBusquedaProfe(e.target.value);
                                    setProfesorSeleccionado(null);
                                    setMostrarSugerencias(true);
                                }}
                                onFocus={() => setMostrarSugerencias(true)}
                            />
                            <div className="input-icon-right">
                                {profesorSeleccionado ? (
                                    profesorSeleccionado.esNuevo ? <Plus size={16} color="green"/> : <Search size={16} color="#0015ff"/>
                                ) : <Search size={16} color="#aaa"/>}
                            </div>

                            {mostrarSugerencias && busquedaProfe && (
                                <ul className="suggestions-list">
                                    {profesoresFiltrados.map(p => (
                                        <li key={p.id} onClick={() => seleccionarProfesor(p)}>{p.nombre}</li>
                                    ))}
                                    {/* Opción para crear nuevo */}
                                    {profesoresFiltrados.every(p => p.nombre.toLowerCase() !== busquedaProfe.toLowerCase()) && (
                                        <li className="create-new-option" onClick={usarNuevoProfesor}>
                                            <Plus size={14}/> Agregar a "<strong>{busquedaProfe}</strong>"
                                        </li>
                                    )}
                                </ul>
                            )}
                        </div>
                    </div>

                    {/* SELECTOR DE MATERIA (Solo existentes) */}
                    <div className="input-group half-width">
                        <label className="input-label"><BookOpen size={16}/> Materia</label>
                        <select 
                            className="custom-input"
                            name="materia_nombre"
                            value={formData.materia_nombre}
                            onChange={handleChange}
                            required
                        >
                            <option value="">Selecciona materia...</option>
                            {materias.map(m => (
                                <option key={m.id} value={m.nombre}>{m.nombre}</option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="sliders-row">
                    <div className="slider-group">
                        <div className="slider-header">
                            <label className="input-label"><Star size={14} fill="#ffb400" color="#ffb400"/> Calif.</label>
                            <span className="slider-value blue">{formData.calificacion}</span>
                        </div>
                        <input 
                            type="range" min="1" max="10" name="calificacion"
                            className="range-slider blue-slider"
                            value={formData.calificacion} onChange={handleSliderChange}
                        />
                    </div>

                    <div className="slider-group">
                        <div className="slider-header">
                            <label className="input-label"><BarChart size={14} color="#ff5722"/> Dif.</label>
                            <span className="slider-value orange">{formData.dificultad}</span>
                        </div>
                        <input 
                            type="range" min="1" max="10" name="dificultad"
                            className="range-slider orange-slider"
                            value={formData.dificultad} onChange={handleSliderChange}
                        />
                    </div>
                </div>

                <div className="input-group">
                    <label className="input-label">Comentario</label>
                    <textarea 
                        className="custom-textarea compact-textarea"
                        name="comentario"
                        placeholder="¿Qué tal explica? Sé respetuoso."
                        value={formData.comentario}
                        onChange={handleChange}
                        required
                    ></textarea>
                </div>

                <div className="form-actions compact-actions">
                    <button type="button" className="btn-cancel" onClick={() => navigate('/resenas')}>Cancelar</button>
                    <button type="submit" className="btn-submit" disabled={loading}>
                        {loading ? 'Publicando...' : <><Save size={18}/> Publicar Reseña</>}
                    </button>
                </div>
            </form>
        </div>
      </main>

      <div className="bottom-navigation-bar">
        <Link to="/portal" className="nav-link"><button className="nav-pill-button">Portal</button></Link>  
        <Link to="/horarios" className="nav-link"><button className="nav-pill-button">Horarios</button></Link>
        <Link to="/menu" className="nav-link"><button className="nav-pill-button">Asistente</button></Link>          
      </div>
    </div>
  );
};

export default AgregarResena;