import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
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

  // URL de tu API 
  const API_URL = "http://127.0.0.1:8000/api/ia/process_reviews";

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
    setEstaArrastrando(true);
  };

  const alSalirDeArrastrar = () => setEstaArrastrando(false);

  const alSoltarArchivo = (e) => {
    e.preventDefault();
    setEstaArrastrando(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validarYProcesarArchivo(e.dataTransfer.files[0]);
    }
  };

  // --- LÓGICA DE CONEXIÓN CON LA API ---
  const handleAnalizar = async () => {
    if (!archivo) {
        alert("Por favor selecciona un archivo primero.");
        return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
        navigate('/login');
        return;
    }

    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    const formData = new FormData();
    formData.append('file', archivo);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            setSuccessMsg(data.message); 
            setReviews(data.data); 
        } else {
            setError(data.detail || "Error al procesar el archivo.");
            if (response.status === 401 || response.status === 403) {
                alert("Sesión expirada o permisos insuficientes.");
                navigate('/login');
            }
        }

    } catch (err) {
        console.error(err);
        setError("Error de conexión con el servidor. Verifica que la API esté corriendo.");
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

            {/* --- TEXTO DE ADVERTENCIA NUEVO --- */}
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

            {/* MENSAJES DE ESTADO */}
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
               ) : reviews.length > 0 ? (
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