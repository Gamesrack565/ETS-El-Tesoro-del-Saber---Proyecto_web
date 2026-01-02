import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig'; // IMPORTANTE: Usar tu instancia de Axios
import './pagina_materias.css'; 

const MallaCurricular = () => {
  // --- ESTADOS DE NAVEGACIÓN Y FILTROS ---
  const [activeTab, setActiveTab] = useState('1-2');
  const [activeCareer, setActiveCareer] = useState('IA');
  const [showOptativas, setShowOptativas] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // --- ESTADOS PARA EL MODAL DE RECURSOS ---
  const [selectedMateria, setSelectedMateria] = useState(null); 
  const [resources, setResources] = useState([]); 
  const [loadingResources, setLoadingResources] = useState(false); 
  const [isModalOpen, setIsModalOpen] = useState(false); 

  const navigate = useNavigate();

  // --- DATOS DE LAS MATERIAS ---
  const data = {
    IA: {
      sem1: ["Fundamentos de Programación", "Matemáticas Discretas", "Cálculo", "Comunicación Oral y Escrita", "Mecánica y Electromagnetismo", "Fundamentos Económicos"],
      sem2: ["Algoritmos y Estructuras de Datos", "Fundamentos de Diseño Digital", "Cálculo Aplicado", "Ingeniería, Ética y Sociedad", "Álgebra Lineal", "Finanzas Empresariales"],
      sem3: ["Análisis y Diseño de Algoritmos", "Paradigmas de Programación", "Ecuaciones Diferenciales", "Bases de Datos", "Diseño de Sistemas Digitales", "Liderazgo Personal"],
      sem4: ["Fundamentos de Inteligencia Artificial", "Probabilidad y Estadística", "Matemáticas Avanzadas para la Ingenieria", "Tecnologías para el Desarrollo de Aplicaciones Web", "Análisis y Diseño de Sistemas", "Procesamiento Digital de Imagenes"],
      sem5: ["Aprendizaje de Máquina", "Visión Artificial", "Teoría de la Computación", "Procesamiento de Señales", "Algoritmos Bioinspirados", "Tecnologías de Lenguaje Natural"],
      sem6: ["Cómputo Paralelo", "Redes Neuronales y Aprendizaje Profundo", "Ingeniería de Software para Sistemas Inteligentes", "Optativa A", "Optativa B", "Metodología de la Investigación y Divulgación Científica"],
      sem7: ["Reconocimiento de Voz", "Trabajo Terminal I", "Formulación y Evaluación de Proyectos Informáticos", "Optativa C", "Optativa D"],
      sem8: ["Gestión Empresarial", "Trabajo Terminal II", "Estancia Profesional", "Desarrollo de Habilidades Sociales para la Alta Dirección"]
    },
    Sistemas: {
      sem1: ["Cálculo", "Análisis Vectorial", "Matemáticas Discretas", "Ingeniería Ética", "Fundamentos Prog.", "Comunicación Oral"],
      sem2: ["Ecuaciones Diferenciales", "Cálculo Aplicado", "Mecánica", "Fundamentos Econ.", "Algoritmos", "Diseño Digital"],
      sem3: [], sem4: [] 
    },
    Datos: {
      sem1: ["Cálculo", "Matemáticas Discretas", "Fundamentos Prog.", "Intro a Ciencia Datos", "Comunicación Oral", "Ética"],
      sem2: ["Álgebra Lineal", "Cálculo Multivariable", "Algoritmos", "Economía", "Probabilidad", "Métodos Numéricos"],
      sem3: [], sem4: []
    }
  };

  const optativasSem6Left = ["Aplicaciones de Lenguaje Natural", "Cómputo en la Nube", "Interacción Humano-Máquina"];
  const optativasSem6Right = ["Minería de Datos", "Programación de Dispositivos Móviles", "Propiedad Intelectual", "Sistemas Multiagentes"];
  const optativasSem7Left = ["Temas Selectos de Inteligencia Artificial", "Tópicos Selectos de Algoritmos Bioinspirados", "Aplicaciones de Inteligencia Artificial en Sistemas Embebidos"];
  const optativasSem7Right = ["Técnicas de Programación para Robots Móviles", "Big Data", "Innovación y Emprendimiento Tecnológico", "Aplicaciones de Sistemas Multiagentes"];

  const currentMaterias = data[activeCareer] || {};

  // --- FUNCIONES DE UTILIDAD ---
  const normalizeText = (text) => {
    return text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  };

  const getHighlightClass = (materiaName) => {
    if (!searchTerm) return '';
    return normalizeText(materiaName).includes(normalizeText(searchTerm)) ? ' highlight-match' : '';
  };

  // --- LÓGICA DE BÚSQUEDA ---
  const handleSearch = (e) => {
    const term = e.target.value;
    setSearchTerm(term);
    if (term === '') return;

    const normalizedTerm = normalizeText(term);
    let foundInStandard = false;

    for (const [semKey, subjects] of Object.entries(currentMaterias)) {
        const found = subjects.some(subject => normalizeText(subject).includes(normalizedTerm));
        if (found) {
            const semNum = parseInt(semKey.replace('sem', ''));
            let newTab = semNum <= 2 ? '1-2' : semNum <= 4 ? '3-4' : semNum <= 6 ? '5-6' : '7-8';
            if (newTab !== activeTab) setActiveTab(newTab);
            setShowOptativas(false);
            foundInStandard = true;
            break; 
        }
    }

    if (!foundInStandard) {
        const optativas6 = [...optativasSem6Left, ...optativasSem6Right];
        if (optativas6.some(sub => normalizeText(sub).includes(normalizedTerm))) {
            setActiveTab('5-6');
            setShowOptativas(true);
            return;
        }
        const optativas7 = [...optativasSem7Left, ...optativasSem7Right];
        if (optativas7.some(sub => normalizeText(sub).includes(normalizedTerm))) {
            setActiveTab('7-8');
            setShowOptativas(true);
            return;
        }
    }
  };

  const handleTabClick = (tab) => {
    setActiveTab(tab);
    setShowOptativas(false);
  };

  // --- API Y MODAL (Corregido con Axios) ---
  const handleMateriaClick = async (materiaName) => {
    setSelectedMateria(materiaName);
    setIsModalOpen(true);
    setLoadingResources(true);
    setResources([]); 

    try {
        // Usamos la instancia 'api' de Axios que ya tiene la URL de Koyeb
        const response = await api.get(`/portal/buscar_por_nombre/?nombre=${encodeURIComponent(materiaName)}`);
        
        // Axios pone los datos en .data automáticamente
        setResources(response.data);
    } catch (error) {
        console.error("Error al obtener recursos:", error);
        setResources([]);
    } finally {
        setLoadingResources(false);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedMateria(null);
  };

  const handleDownload = (resource) => {
      // Obtenemos la URL del recurso desde el objeto
      let urlDestino = resource.path || resource.url_or_path;
      
      if (!urlDestino) {
          alert("Error: No se encontró la ruta del recurso.");
          return;
      }

      if (resource.type === 'link' || resource.type === 'video') {
          if (!urlDestino.match(/^https?:\/\//i)) {
              urlDestino = 'https://' + urlDestino;
          }
          window.open(urlDestino, '_blank', 'noopener,noreferrer');
      } 
      else {
          // Para descargas de archivos locales, usamos el endpoint de descarga
          // Obtenemos la base URL desde la configuración de axios
          const baseUrl = api.defaults.baseURL;
          const downloadUrl = `${baseUrl}/portal/download/${resource.id}`;
          window.open(downloadUrl, '_blank');
      }
  };

  const goToUpload = () => {
    if (selectedMateria) {
        navigate('/subir-recurso', { state: { materia: selectedMateria } });
    } else {
        navigate('/subir-recurso');
    }
  };

  return (
    <div className="malla-curricular-container">
      
      {/* MODAL */}
      {isModalOpen && (
          <div className="modal-overlay" onClick={closeModal}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                  <div className="modal-header">
                      <h2>Recursos de: {selectedMateria}</h2>
                      <button className="modal-close-btn" onClick={closeModal}>✖</button>
                  </div>
                  
                  <div className="modal-body">
                      {loadingResources ? (
                          <div className="spinner">Cargando recursos...</div>
                      ) : (
                          <>
                            {resources.length > 0 ? (
                                <ul className="resource-list">
                                    {resources.map((res) => (
                                        <li key={res.id} className="resource-item">
                                            <div className="resource-info">
                                                <span className="resource-icon">
                                                    {res.type === 'pdf' ? '📄' : res.type === 'video' ? '🎥' : '🔗'}
                                                </span>
                                                <div>
                                                    <strong>{res.title}</strong>
                                                    <p className="resource-desc">{res.description || "Sin descripción"}</p>
                                                </div>
                                            </div>
                                            <button 
                                                className="btn-download"
                                                onClick={() => handleDownload(res)}
                                            >
                                                {res.type === 'link' || res.type === 'video' ? 'Abrir' : 'Descargar'}
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <div className="no-resources">
                                    <span style={{fontSize: '30px'}}>📂</span>
                                    <p>No hay recursos subidos para esta materia aún.</p>
                                    <p className="subtext">¡Sé el primero en aportar!</p>
                                </div>
                            )}

                            <div className="modal-upload-section">
                                <div className="upload-separator"></div>
                                <p className="upload-prompt">¿Tienes apuntes, guías o videos útiles?</p>
                                <button className="btn-upload-modal" onClick={goToUpload}>
                                    📤 Subir Archivos para esta materia
                                </button>
                            </div>
                          </>
                      )}
                  </div>
              </div>
          </div>
      )}

      {/* HEADER */}
      <div className="sticky-header">
          <button className="btn-upload-header" onClick={() => navigate('/subir-recurso')}>
              ☁ Sube tus archivos aquí
          </button>
          <button className="btn-go-menu" onClick={() => navigate('/menu')}>
              Menú Principal ➝
          </button>

          <h1 className="main-title">Buscador</h1>
          
          <p className="click-instruction">
            Da click en cualquier materia para acceder a sus recursos
          </p>

          <div className="search-bar-container">
            <span className="search-icon">🔍</span>
            <input 
                type="text" 
                className="search-input" 
                placeholder="Buscar materia..." 
                value={searchTerm}
                onChange={handleSearch}
            />
            <span className="close-icon" onClick={() => setSearchTerm('')} style={{cursor: 'pointer'}}>✖</span>
          </div>

          <div className="career-filters">
            <button className={`career-filter ${activeCareer === 'Sistemas' ? 'active' : ''}`} onClick={() => setActiveCareer('Sistemas')}>
                Ingeniería en Sistemas Computacionales
            </button>
            <button className={`career-filter ${activeCareer === 'IA' ? 'active' : ''}`} onClick={() => setActiveCareer('IA')}>
                Ingeniería en Inteligencia Artificial
            </button>
            <button className={`career-filter ${activeCareer === 'Datos' ? 'active' : ''}`} onClick={() => setActiveCareer('Datos')}>
                Licenciatura en Ciencias de Datos
            </button>
          </div>

          <div className="semester-tabs-container">
            <div className="semester-label">Semestre:</div>
            <div className="tabs-wrapper">
                <div className="tabs">
                    <button className={`tab ${activeTab === '1-2' ? 'active' : ''}`} onClick={() => handleTabClick('1-2')}>1 - 2</button>
                    <button className={`tab ${activeTab === '3-4' ? 'active' : ''}`} onClick={() => handleTabClick('3-4')}>3 - 4</button>
                    <button className={`tab ${activeTab === '5-6' ? 'active' : ''}`} onClick={() => handleTabClick('5-6')}>5 - 6</button>
                    <button className={`tab ${activeTab === '7-8' ? 'active' : ''}`} onClick={() => handleTabClick('7-8')}>7 - 8</button>
                </div>
                {(activeTab === '5-6' || activeTab === '7-8') && (
                    <button className="optativas-tab" onClick={() => setShowOptativas(true)}>Optativas</button>
                )}
            </div>
          </div>
          <div className="header-border-line"></div>
      </div>

      {/* CONTENIDO */}
      <div className="tab-content">
        
        {activeTab === '1-2' && (
          <div className="curriculum-grid">
            <div className="semester-column">
              <h2 className="semester-number">1</h2>
              {currentMaterias.sem1?.map((m, i) => 
                <div key={i} className={`subject-pill${getHighlightClass(m)}`} onClick={() => handleMateriaClick(m)}>{m}</div>
              )}
            </div>
            <div className="semester-column">
              <h2 className="semester-number">2</h2>
              {currentMaterias.sem2?.map((m, i) => 
                <div key={i} className={`subject-pill${getHighlightClass(m)}`} onClick={() => handleMateriaClick(m)}>{m}</div>
              )}
            </div>
          </div>
        )}


        {activeTab === '3-4' && (
          <div className="curriculum-grid">
            <div className="semester-column">
              <h2>3</h2>
              {currentMaterias.sem3?.map((m, i) =>
                <div key={i} className={`subject-pill${getHighlightClass(m)}`} onClick={() => handleMateriaClick(m)}>{m}</div>
              )}
            </div>
            <div className="semester-column">
              <h2>4</h2>
              {currentMaterias.sem4?.map((m, i) =>
                <div key={i} className={`subject-pill${getHighlightClass(m)}`} onClick={() => handleMateriaClick(m)}>{m}</div>
              )}
            </div>
          </div>
        )}

        {activeTab === '5-6' && !showOptativas && (
          <div className="curriculum-grid">
            <div className="semester-column">
              <h2 className="semester-number">5</h2>
              {currentMaterias.sem5?.map((m, i) => 
                <div key={i} className={`subject-pill${getHighlightClass(m)}`} onClick={() => handleMateriaClick(m)}>{m}</div>
              )}
            </div>
            <div className="semester-column">
              <h2 className="semester-number">6</h2>
              {currentMaterias.sem6?.map((m, i) => 
                <div key={i} className={`subject-pill${getHighlightClass(m)}`} onClick={() => handleMateriaClick(m)}>{m}</div>
              )}
            </div>
          </div>
        )}

        {activeTab === '5-6' && showOptativas && (
          <div>
              <h2 className="optativas-title">Materias optativas de 6to semestre</h2>
              <div className="optativas-columns">
                  <div className="semester-column">
                      {optativasSem6Left.map((m, i) => <div key={i} className={`subject-pill optativa-pill${getHighlightClass(m)}`} onClick={() => handleMateriaClick(m)}>{m}</div>)}
                  </div>
                  <div className="semester-column">
                      {optativasSem6Right.map((m, i) => <div key={i} className={`subject-pill optativa-pill${getHighlightClass(m)}`} onClick={() => handleMateriaClick(m)}>{m}</div>)}
                  </div>
              </div>
          </div>
        )}

        {activeTab === '7-8' && !showOptativas && (
            <div className="curriculum-grid">
             <div className="semester-column">
              <h2 className="semester-number">7</h2>
              {currentMaterias.sem7?.map((m, i) => 
                <div key={i} className={`subject-pill${getHighlightClass(m)}`} onClick={() => handleMateriaClick(m)}>{m}</div>
              )}
            </div>
            <div className="semester-column">
              <h2 className="semester-number">8</h2>
              {currentMaterias.sem8?.map((m, i) => 
                <div key={i} className={`subject-pill${getHighlightClass(m)}`} onClick={() => handleMateriaClick(m)}>{m}</div>
              )}
            </div>
          </div>
        )}

        {activeTab === '7-8' && showOptativas && (
          <div>
              <h2 className="optativas-title">Materias optativas de 7mo semestre</h2>
              <div className="optativas-columns">
                  <div className="semester-column">
                      {optativasSem7Left.map((m, i) => <div key={i} className={`subject-pill optativa-pill${getHighlightClass(m)}`} onClick={() => handleMateriaClick(m)}>{m}</div>)}
                  </div>
                  <div className="semester-column">
                      {optativasSem7Right.map((m, i) => <div key={i} className={`subject-pill optativa-pill${getHighlightClass(m)}`} onClick={() => handleMateriaClick(m)}>{m}</div>)}
                  </div>
              </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MallaCurricular;