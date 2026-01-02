import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig'; // Importamos tu instancia de axios personalizada
import './pagina_analisis.css';

const Pagina_Analisis = () => {
  const [archivo, setArchivo] = useState(null);
  const [estaArrastrando, setEstaArrastrando] = useState(false);
  
  // --- ESTADOS PARA LA API ---
  const [loading, setLoading] = useState(false);
  const [reviews, setReviews] = useState([]); 
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const inputRef = useRef(null);
  const navigate = useNavigate();

  // Verificar sesión al entrar
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
        alert("Necesitas iniciar sesión como Administrador para usar esta herramienta.");
        navigate('/login');
    }
  }, [navigate]);

  const abrirSelector = () => inputRef.current.click();

  const validarYProcesarArchivo = (file) => {
    if (!file) return;
    if (file.name.endsWith('.txt') || file.type === "text/plain") {
      setArchivo(file);
      setError(null);
      setSuccessMsg(null);
      setReviews([]); 
    } else {
      alert("Error: Solo se permiten archivos de texto (.txt)");
      setArchivo(null);
    }
  };

  const alCambiarArchivo = (e) => validarYProcesarArchivo(e.target.files[0]);

  const alArrastrarSobre = (e) => {
    e.preventDefault();
    estaArrastrando || setEstaArrastrando(true);
  };

  const alSalirDeArrastrar = () => setEstaArrastrando(false);

  const alSoltarArchivo = (e) => {
    e.preventDefault();
    setEstaArrastrando(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validarYProcesarArchivo(e.dataTransfer.files[0]);
    }
  };

  // --- LÓGICA DE CONEXIÓN CON LA API UTILIZANDO AXIOS ---
  const handleAnalizar = async () => {
    if (!archivo) {
        alert("Por favor selecciona un archivo primero.");
        return;
    }

    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    const formData = new FormData();
    formData.append('file', archivo);

    try {
        // Usamos la instancia 'api'. El interceptor agregará automáticamente el Token.
        // La ruta es relativa a la baseURL (que ya termina en /api)
        const response = await api.post('/ia/process_reviews', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        // Con Axios, los datos están en response.data
        setSuccessMsg(response.data.message); 
        setReviews(response.data.data); 

    } catch (err) {
        console.error("Error en el análisis:", err);
        
        // Manejo de errores detallado con Axios
        if (err.response) {
            const status = err.response.status;
            const detail = err.response.data?.detail;

            if (status === 401 || status === 403) {
                setError("No tienes permisos suficientes o tu sesión expiró.");
                alert("Sesión no válida.");
                navigate('/login');
            } else {
                setError(detail || "Error al procesar el archivo en el servidor.");
            }
        } else {
            setError("Error de conexión con el servidor de Koyeb.");
        }
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="analisis-page-container">
      <header className="analisis-header">
        <h1>Análisis de mensajes de texto</h1>
      </header>

      <main className="analisis-main-content">
        <div className="two-column-layout">
          
          {/* COLUMNA IZQUIERDA: SUBIR */}
          <section className="analisis-column">
            <h2 className="column-title">
              Sube el historial de chat (.txt)
            </h2>

            <p className="admin-warning">
                Debes ser admin para usar esta función
            </p>
            
            <div 
              className={`data-box upload-box ${estaArrastrando ? 'dragging' : ''} ${archivo ? 'has-file' : ''}`}
              onDragOver={alArrastrarSobre}
              onDragLeave={alSalirDeArrastrar}
              onDrop={alSoltarArchivo}
              onClick={abrirSelector}
            >
              <input 
                type="file" 
                ref={inputRef} 
                onChange={alCambiarArchivo} 
                accept=".txt" 
                style={{ display: 'none' }} 
              />
              
              <span className="upload-text">
                {archivo ? `✅ ${archivo.name}` : "Arrastra tu archivo aquí o haz clic"}
              </span>
            </div>

            {error && <div className="status-msg error">{error}</div>}
            {successMsg && <div className="status-msg success">{successMsg}</div>}

            <button 
                className="analisis-button primary-button" 
                onClick={handleAnalizar}
                disabled={loading || !archivo}
            >
              {loading ? "ANALIZANDO CON IA..." : "ANALIZAR CHAT"}
            </button>
          </section>

          {/* COLUMNA DERECHA: RESULTADOS */}
          <section className="analisis-column">
            <h2 className="column-title">Reseñas Obtenidas</h2>
            
            <div className="data-box results-box">
               {loading ? (
                   <div className="spinner-container">
                       <div className="spinner"></div>
                       <p>La IA está leyendo el chat...</p>
                   </div>
               ) : reviews && reviews.length > 0 ? (
                   <div className="reviews-list">
                       {reviews.map((rev, index) => (
                           <div key={index} className="review-card-item">
                               <div className="review-header-card">
                                   <span className="prof-name">👨‍🏫 {rev.profesor_nombre}</span>
                                   <span className="rating-badge">⭐ {rev.calificacion}</span>
                               </div>
                               <p className="review-body">"{rev.comentario}"</p>
                               <div className="review-meta">
                                   <span>Dificultad: {rev.dificultad}/10</span>
                                   <span>Autor: {rev.autor_original}</span>
                               </div>
                           </div>
                       ))}
                   </div>
               ) : (
                   <div className="empty-state">
                       <p>{successMsg ? "No se encontraron reseñas en el chat." : "Los resultados aparecerán aquí..."}</p>
                   </div>
               )}
            </div>
            
            <div style={{ height: '45px', flexShrink: 0 }}></div> 
          </section>
        </div>
      </main>

      <footer className="analisis-footer">
        <Link to="/menu" className="no-underline">
            <button className="analisis-button secondary-button">
              Regresar al menú principal
            </button>
        </Link>
      </footer>
    </div>
  );
};

export default Pagina_Analisis;