import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig'; // Importamos tu configuración de Axios
import './pagina_subir.css';

const Pagina_Subir = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  // --- ESTADOS DEL FORMULARIO ---
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [materia, setMateria] = useState('');
  const [type, setType] = useState('pdf'); 
  const [urlExterna, setUrlExterna] = useState('');
  const [archivo, setArchivo] = useState(null);

  // Estados visuales
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null); 

  // AL CARGAR: Verificamos sesión y pre-llenamos materia
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
        alert("Debes iniciar sesión para subir recursos.");
        navigate('/login');
    }

    if (location.state && location.state.materia) {
      setMateria(location.state.materia);
    }
  }, [location, navigate]);

  // --- MANEJO DE ARCHIVOS ---
  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = () => { setIsDragging(false); };
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setArchivo(e.dataTransfer.files[0]);
    }
  };
  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setArchivo(e.target.files[0]);
    }
  };
  const openFileSelector = () => fileInputRef.current.click();

  // --- ENVÍO DEL FORMULARIO CON AXIOS ---
  const handleSubmit = async () => {
    // 1. Validaciones
    if (!title || !materia || !type) {
      setMessage({ type: 'error', text: 'Por favor completa Título, Materia y Tipo.' });
      return;
    }

    if ((type === 'pdf' || type === 'image') && !archivo) {
      setMessage({ type: 'error', text: 'Debes subir un archivo para este tipo de recurso.' });
      return;
    }

    if ((type === 'link' || type === 'video') && !urlExterna) {
      setMessage({ type: 'error', text: 'Debes ingresar una URL válida.' });
      return;
    }

    setLoading(true);
    setMessage(null);

    // 2. Construir FormData
    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description); 
    formData.append('materia_nombre', materia);
    formData.append('type', type);

    if (type === 'pdf' || type === 'image') {
      formData.append('file', archivo);
    } else {
      formData.append('url_externa', urlExterna);
    }

    // 3. Petición con la instancia 'api'
    try {
      // Usamos la ruta relativa al baseURL de tu axiosConfig
      const response = await api.post('/portal/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
            // El token se envía automáticamente gracias al Interceptor en axiosConfig
        }
      });

      // Éxito con Axios
      setMessage({ type: 'success', text: '¡Recurso subido exitosamente!' });
      
      // Limpiamos
      setTitle('');
      setDescription('');
      setArchivo(null);
      setUrlExterna('');
      
      setTimeout(() => navigate('/portal'), 1500);

    } catch (error) {
      console.error("Error al subir:", error);
      
      if (error.response) {
        // El servidor respondió con error (4xx o 5xx)
        const status = error.response.status;
        const detail = error.response.data?.detail;

        if (status === 401) {
            setMessage({ type: 'error', text: 'Tu sesión ha expirado. Redirigiendo...' });
            setTimeout(() => navigate('/login'), 2000);
        } else {
            setMessage({ type: 'error', text: `Error: ${detail || 'No se pudo subir.'}` });
        }
      } else {
        // Error de conexión (Koyeb caído o sin internet)
        setMessage({ type: 'error', text: 'Error de conexión con el servidor.' });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="subir-page-container">
      <header className="subir-header">
        <h1>Portal de Estudio - Subir Recurso</h1>
      </header>

      <main className="subir-main-content">
        <div className="two-column-layout">
          
          <section className="subir-column">
            <h2 className="column-title">Detalles del Recurso</h2>
            
            <div className="form-box">
              <div>
                  <label>Materia *</label>
                  <input 
                    type="text" 
                    className="input-field" 
                    placeholder="Ej. Bases de Datos"
                    value={materia}
                    onChange={(e) => setMateria(e.target.value)}
                  />
              </div>

              <div>
                  <label>Título *</label>
                  <input 
                    type="text" 
                    className="input-field" 
                    placeholder="Ej. Apuntes Parcial 1"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                  />
              </div>

              <div>
                  <label>Descripción</label>
                  <textarea 
                    className="input-field textarea-field" 
                    placeholder="Contenido breve..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
              </div>

              <div>
                  <label>Tipo de Recurso *</label>
                  <select 
                    className="input-field select-field"
                    value={type}
                    onChange={(e) => {
                        setType(e.target.value);
                        setArchivo(null);
                        setUrlExterna('');
                    }}
                  >
                    <option value="pdf">Documento PDF</option>
                    <option value="image">Imagen</option>
                    <option value="link">Enlace Web</option>
                    <option value="video">Video</option>
                  </select>
              </div>
            </div>
          </section>

          <section className="subir-column">
            <h2 className="column-title">
              {type === 'pdf' || type === 'image' ? 'Archivo' : 'Enlace'}
            </h2>
            
            <div className="action-box-container">
                {(type === 'pdf' || type === 'image') && (
                    <div 
                        className={`data-box upload-box ${isDragging ? 'dragging' : ''} ${archivo ? 'has-file' : ''}`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        onClick={openFileSelector}
                    >
                        <input 
                            type="file" 
                            ref={fileInputRef} 
                            onChange={handleFileSelect} 
                            accept={type === 'pdf' ? ".pdf" : "image/*"} 
                            style={{ display: 'none' }} 
                        />
                        <span className="upload-icon">
                            {archivo ? '✅' : (type === 'pdf' ? '📄' : '🖼️')}
                        </span>
                        <span className="upload-text">
                            {archivo ? archivo.name : `Click o Arrastra tu ${type.toUpperCase()}`}
                        </span>
                    </div>
                )}

                {(type === 'link' || type === 'video') && (
                    <div className="data-box url-box">
                        <span className="upload-icon">🔗</span>
                        <input 
                            type="url" 
                            className="input-field" 
                            placeholder="https://..."
                            value={urlExterna}
                            onChange={(e) => setUrlExterna(e.target.value)}
                        />
                    </div>
                )}

                <div style={{ width: '100%' }}>
                    {message && (
                        <div className={`status-message ${message.type}`}>
                            {message.text}
                        </div>
                    )}

                    <button 
                        className="subir-button primary-button" 
                        onClick={handleSubmit}
                        disabled={loading}
                    >
                        {loading ? 'SUBIENDO...' : 'PUBLICAR'}
                    </button>
                </div>
            </div>
          </section>
        </div>
      </main>

      <footer className="subir-footer">
        <Link to="/portal" className="no-underline">
            <button className="subir-button secondary-button">
              Cancelar
            </button>
        </Link>
      </footer>
    </div>
  );
};

export default Pagina_Subir;