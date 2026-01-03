import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, Trash2, Edit2, Check, X, Plus, Settings, Coffee, Calendar, Save, LogOut, User, RefreshCw } from 'lucide-react'; 
import api from '../../api/axiosConfig'; 
import './pagina_horario.css'; 

const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

const COLORES_MATERIAS = [
    '#ffadad', '#ffd6a5', '#fdffb6', '#caffbf', '#9bf6ff', '#a0c4ff', '#bdb2ff', '#ffc6ff', '#ff9aa2', '#e2f0cb'
];

const CalendariosHorarios = () => {
  const navigate = useNavigate();
  
  // --- ESTADOS DE DATOS ---
  const [materiasBackend, setMateriasBackend] = useState([]); 
  const [user, setUser] = useState(null);
  const [loadingInitial, setLoadingInitial] = useState(true);
  
  // --- ESTADOS DE LA INTERFAZ (GRID) ---
  const [filtro, setFiltro] = useState("");
  
  // ESTOS DOS SON LA CLAVE DE LA EDICIÓN:
  const [horario, setHorario] = useState({}); // { "Lunes-1": {materia}, ... }
  const [timeSlots, setTimeSlots] = useState([]); // [{id:1, start:'07:00', end:'08:30'}, ...]

  const [draggedMateria, setDraggedMateria] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [horarioIdActual, setHorarioIdActual] = useState(null); // ID del horario en BD (si existe)
  
  // --- CONFIGURACIÓN ---
  const [showConfig, setShowConfig] = useState(false);
  const [classDuration, setClassDuration] = useState(60);
  const [breaks, setBreaks] = useState([]);
  const [newBreak, setNewBreak] = useState({ start: '', end: '' });
  
  const [editingSlotId, setEditingSlotId] = useState(null);
  const [tempSlotData, setTempSlotData] = useState({ start: '', end: '' });

  // =========================================================
  // 1. CARGA INICIAL INTELIGENTE
  // =========================================================
  useEffect(() => {
      const init = async () => {
          checkUserSession();
          const materiasList = await fetchMaterias();
          const cargoHorario = await cargarHorarioExistente(materiasList);
          
          if (!cargoHorario) {
              console.log("No se encontró horario previo, generando plantilla base...");
              generarHorarioBase();
          } else {
              console.log("Horario recuperado exitosamente.");
          }
          setLoadingInitial(false);
      };
      init();
  }, []);

  const checkUserSession = () => {
      const token = localStorage.getItem('token');
      if (token) {
          const savedName = localStorage.getItem('user_full_name') || "Estudiante";
          setUser({ name: savedName.split(' ')[0] });
      }
  };

  const handleLogout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('user_full_name');
      setUser(null);
      navigate('/login');
  };

  const fetchMaterias = async () => {
      try {
          const response = await api.get('/catalogos/materias/?limit=200');
          const conColor = response.data.map((m, index) => ({
              ...m,
              color: COLORES_MATERIAS[index % COLORES_MATERIAS.length]
          }));
          setMateriasBackend(conColor);
          return conColor;
      } catch (error) {
          console.error("Error materias:", error);
          return [];
      }
  };

  // --- LÓGICA CORE: RECONSTRUIR HORARIO DESDE BD ---
  const cargarHorarioExistente = async (listaMaterias) => {
      try {
          const res = await api.get('/horarios/');
          if (!res.data || res.data.length === 0) return false;

          const miHorarioBD = res.data[res.data.length - 1];
          setHorarioIdActual(miHorarioBD.id);

          // 1. Recolectar todos los intervalos únicos (inicio-fin)
          const intervalosSet = new Set();
          miHorarioBD.items.forEach(item => {
              if (item.hora_grupo && item.hora_grupo.includes("-")) {
                  // Lógica para extraer hora: "Lunes 07:00 - 08:30"
                  // Usamos regex para ser más precisos
                  const match = item.hora_grupo.match(/(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})/);
                  if (match) {
                      intervalosSet.add(`${match[1]}-${match[2]}`);
                  }
              }
          });

          if (intervalosSet.size === 0) return false;

          // 2. Ordenar intervalos por hora de inicio
          let intervalosOrdenados = Array.from(intervalosSet).map(str => {
              const [start, end] = str.split('-');
              return { start, end };
          }).sort((a, b) => a.start.localeCompare(b.start));

          // 3. RECONSTRUIR HUECOS (DESCANSOS)
          // Si hay un espacio entre el fin de uno y el inicio del siguiente, es un break.
          let slotsFinales = [];
          let idCounter = 1;

          for (let i = 0; i < intervalosOrdenados.length; i++) {
              const actual = intervalosOrdenados[i];
              
              // Agregar el slot de clase actual
              slotsFinales.push({ id: idCounter++, start: actual.start, end: actual.end, type: 'class' });

              // Mirar el siguiente para ver si hay hueco
              if (i < intervalosOrdenados.length - 1) {
                  const siguiente = intervalosOrdenados[i+1];
                  if (actual.end < siguiente.start) {
                      // ¡HUECO DETECTADO! Agregamos break
                      slotsFinales.push({ 
                          id: `break-${idCounter++}`, 
                          start: actual.end, 
                          end: siguiente.start, 
                          type: 'break' 
                      });
                  }
              }
          }

          setTimeSlots(slotsFinales);

          // 4. Llenar el grid de materias
          const nuevoStateHorario = {};
          miHorarioBD.items.forEach(item => {
              if (!item.hora_grupo) return;
              
              // Regex para extraer día y hora inicio
              // Ej: "Lunes 07:00 - 08:30" -> Dia: "Lunes", Inicio: "07:00"
              const match = item.hora_grupo.match(/^(.+?)\s+(\d{2}:\d{2})/);
              if (match) {
                  const dia = match[1].trim();
                  const horaInicio = match[2];
                  
                  // Buscar el slot que coincida con esa hora de inicio
                  const slotMatch = slotsFinales.find(s => s.start === horaInicio && s.type === 'class');

                  if (slotMatch) {
                      const key = `${dia}-${slotMatch.id}`;
                      const materiaFull = listaMaterias.find(m => m.id === item.materia_id);
                      nuevoStateHorario[key] = materiaFull || {
                          id: item.materia_id,
                          nombre: item.materia_nombre || "Materia",
                          color: '#e0e0e0'
                      };
                  }
              }
          });

          setHorario(nuevoStateHorario);
          return true;
      } catch (error) {
          console.error("Error recuperando horario:", error);
          return false;
      }
  };

  const addMinutes = (time, mins) => {
      if (!time) return "00:00";
      const [h, m] = time.split(':').map(Number);
      const date = new Date(); date.setHours(h, m + mins, 0);
      return date.toTimeString().slice(0, 5);
  };

  const generarHorarioBase = () => {
      let slots = [];
      let currentTime = "07:00"; 
      const endTimeLimit = "22:00"; 
      let idCounter = 1;
      const sortedBreaks = [...breaks].sort((a, b) => a.start.localeCompare(b.start));

      while (currentTime < endTimeLimit) {
          const activeBreak = sortedBreaks.find(b => b.start === currentTime);
          if (activeBreak) {
              slots.push({ id: `break-${idCounter++}`, start: activeBreak.start, end: activeBreak.end, type: 'break' });
              currentTime = activeBreak.end;
          } else {
              const nextTime = addMinutes(currentTime, parseInt(classDuration));
              const nextBreak = sortedBreaks.find(b => b.start > currentTime && b.start < nextTime);
              let slotEnd = nextTime;
              if (nextBreak) slotEnd = nextBreak.start;
              slots.push({ id: idCounter++, start: currentTime, end: slotEnd, type: 'class' });
              currentTime = slotEnd;
          }
      }
      setTimeSlots(slots);
      setHorario({}); 
      setShowConfig(false);
  };

  const guardarHorario = async () => {
      if (!user) { alert("Inicia sesión para guardar."); navigate('/login'); return; }
      const nombreHorario = prompt("Nombre para tu horario:", "Mi Horario Semestral");
      if (!nombreHorario) return;

      setIsSaving(true);
      const itemsParaGuardar = Object.entries(horario).map(([key, materia]) => {
          const [dia, slotId] = key.split('-');
          const slot = timeSlots.find(s => s.id.toString() === slotId.toString());
          const horaString = slot ? `${dia} ${slot.start} - ${slot.end}` : null;
          if (!horaString) return null;
          return { materia_id: materia.id, hora_grupo: horaString };
      }).filter(item => item !== null);

      if (itemsParaGuardar.length === 0) {
          alert("El horario está vacío."); setIsSaving(false); return;
      }

      try {
          if (horarioIdActual) { await api.delete(`/horarios/${horarioIdActual}`); }
          const res = await api.post('/horarios/', { nombre: nombreHorario, items: itemsParaGuardar });
          setHorarioIdActual(res.data.id); 
          alert("¡Horario guardado correctamente!");
      } catch (error) {
          console.error("Error al guardar:", error);
          alert("Hubo un error al guardar.");
      } finally {
          setIsSaving(false);
      }
  };

  const handleDragStart = (e, materia) => { setDraggedMateria(materia); e.dataTransfer.effectAllowed = "copy"; };
  const handleDragOver = (e) => { e.preventDefault(); e.dataTransfer.dropEffect = "copy"; };
  const handleDrop = (e, dia, slotId, type) => {
    e.preventDefault();
    if (type === 'break' && (dia !== 'Sábado' && dia !== 'Domingo')) return; 
    if (draggedMateria) {
        const key = `${dia}-${slotId}`;
        setHorario(prev => ({ ...prev, [key]: draggedMateria }));
    }
    setDraggedMateria(null);
  };
  const handleRemoveItem = (dia, slotId) => {
      const key = `${dia}-${slotId}`;
      const nuevo = { ...horario }; delete nuevo[key]; setHorario(nuevo);
  };
  const addBreak = () => { if(newBreak.start && newBreak.end) { setBreaks([...breaks, newBreak]); setNewBreak({ start: '', end: '' }); } };
  const removeBreak = (index) => { const n = [...breaks]; n.splice(index, 1); setBreaks(n); };
  const addNewSlot = () => {
      const lastSlot = timeSlots[timeSlots.length - 1];
      const start = lastSlot ? lastSlot.end : "07:00";
      const end = addMinutes(start, 60);
      const newId = timeSlots.length > 0 ? Math.max(...timeSlots.map(s => s.id)) + 1 : 1;
      setTimeSlots([...timeSlots, { id: newId, start, end, type: 'class' }]);
  };
  const saveSlot = (id) => { 
      setTimeSlots(prev => prev.map(s => s.id === id ? { ...s, start: tempSlotData.start, end: tempSlotData.end } : s)); 
      setEditingSlotId(null); 
  };

  const materiasFiltradas = materiasBackend.filter(m => m.nombre.toLowerCase().includes(filtro.toLowerCase()));

  if (loadingInitial) {
      return (
          <div className="page-container" style={{justifyContent:'center', alignItems:'center'}}>
              <div style={{textAlign:'center'}}>
                  <RefreshCw className="spin-anim" size={40} color="#240090"/>
                  <p style={{marginTop: 10, fontWeight: 600, color: '#240090'}}>Cargando tu horario...</p>
              </div>
          </div>
      );
  }

  return (
    <div className="page-container">
      
      <header className="fixed-header">
        <h1 className="page-title">Constructor de Horarios</h1>
        <div className="top-buttons">
            
            {/* BOTÓN CALENDARIO IPN CON LINK */}
            <Link to="/calendario" style={{textDecoration:'none'}}>
                <button className="btn-top btn-outline">
                    <Calendar size={16} style={{marginRight: 5}}/> Calendario IPN
                </button>
            </Link>

            <button className="btn-top btn-config" onClick={() => setShowConfig(!showConfig)}>
                <Settings size={16} style={{marginRight: 5}}/> Configuración
            </button>
            
            <button className="btn-top btn-filled" onClick={guardarHorario} disabled={isSaving}>
                {isSaving ? 'Guardando...' : <><Save size={16} style={{marginRight:5}}/> Guardar</>}
            </button>

            <button className="btn-top btn-config" onClick={generarHorarioBase} title="Reiniciar plantilla">
                <RefreshCw size={16}/>
            </button>

            {user ? (
                <div className="user-widget-mini">
                    <span>Hola, <strong>{user.name}</strong></span>
                    <button onClick={handleLogout} className="logout-mini" title="Salir"><LogOut size={14}/></button>
                </div>
            ) : (
                <Link to="/login" className="login-btn-mini"><User size={14}/> Entrar</Link>
            )}
        </div>
      </header>

      {/* --- PANEL DE CONFIGURACIÓN --- */}
      {showConfig && (
          <div className="config-panel-overlay">
              <div className="config-panel">
                  <div className="config-header">
                      <h3>Configuración Global del Horario</h3>
                      <button className="close-config" onClick={() => setShowConfig(false)}><X size={20}/></button>
                  </div>
                  <div className="config-body">
                      <div className="config-item">
                          <label>Duración de Clases</label>
                          <div className="input-with-unit">
                              <input type="number" value={classDuration} onChange={(e) => setClassDuration(e.target.value)} className="clean-input number-input"/>
                              <span>minutos</span>
                          </div>
                      </div>
                      <div className="config-item">
                          <label>Agregar Descanso (Lun - Vie)</label>
                          <div className="break-inputs">
                              <input type="time" value={newBreak.start} onChange={(e) => setNewBreak({...newBreak, start: e.target.value})} className="clean-input time-input"/>
                              <span className="separator">a</span>
                              <input type="time" value={newBreak.end} onChange={(e) => setNewBreak({...newBreak, end: e.target.value})} className="clean-input time-input"/>
                              <button className="btn-add-break" onClick={addBreak}><Plus size={16}/> Agregar</button>
                          </div>
                          {breaks.length > 0 && (
                              <div className="breaks-chip-list">
                                  {breaks.map((b, idx) => (
                                      <div key={idx} className="break-chip">
                                          <Coffee size={12}/> {b.start} - {b.end}
                                          <button onClick={() => removeBreak(idx)}><X size={12}/></button>
                                      </div>
                                  ))}
                              </div>
                          )}
                      </div>
                  </div>
                  <div className="config-footer">
                      <button className="btn-apply-large" onClick={generarHorarioBase}>Aplicar Cambios y Regenerar</button>
                  </div>
              </div>
          </div>
      )}

      <div className="main-dashboard">
        {/* SIDEBAR */}
        <aside className="sidebar-tools">
            <div className="sidebar-header">
                <h2 className="section-label">Materias Disponibles</h2>
                <div className="search-box">
                    <Search size={18} className="search-icon"/>
                    <input type="text" placeholder="Buscar materia..." value={filtro} onChange={(e) => setFiltro(e.target.value)}/>
                </div>
            </div>
            <div className="draggable-list">
                {materiasBackend.length === 0 && <p className="hint-text">Cargando materias...</p>}
                {materiasFiltradas.slice(0, 50).map(m => (
                    <div key={m.id} className="draggable-item" draggable onDragStart={(e) => handleDragStart(e, m)} style={{ borderLeft: `4px solid ${m.color}` }}>
                        <span className="materia-name">{m.nombre}</span>
                    </div>
                ))}
            </div>
        </aside>

        {/* GRID HORARIO */}
        <main className="schedule-panel">
            <div className="schedule-grid-wrapper">
                <div className="schedule-grid" style={{ gridTemplateRows: `40px repeat(${timeSlots.length}, minmax(60px, auto))` }}>
                    <div className="grid-header-corner">Hora</div>
                    {DIAS.map(d => <div key={d} className={`grid-header-day ${d === 'Sábado' || d === 'Domingo' ? 'weekend' : ''}`}>{d}</div>)}

                    {timeSlots.map((slot) => (
                        <React.Fragment key={slot.id}>
                            <div className={`grid-hour-label ${slot.type === 'break' ? 'break-label' : ''}`}>
                                {editingSlotId === slot.id ? (
                                    <div className="hour-edit-form">
                                        <input type="text" value={tempSlotData.start} className="mini-input" onChange={(e) => setTempSlotData({...tempSlotData, start: e.target.value})}/>
                                        <input type="text" value={tempSlotData.end} className="mini-input" onChange={(e) => setTempSlotData({...tempSlotData, end: e.target.value})}/>
                                        <button className="mini-btn-save" onClick={() => saveSlot(slot.id)}><Check size={12}/></button>
                                    </div>
                                ) : (
                                    <>
                                        <span>{slot.start} - {slot.end}</span>
                                        {slot.type === 'break' && <span className="break-tag">RECREO</span>}
                                        <button className="edit-h-btn" onClick={() => { setEditingSlotId(slot.id); setTempSlotData({start: slot.start, end: slot.end}); }}><Edit2 size={10}/></button>
                                    </>
                                )}
                            </div>
                            {DIAS.map(dia => {
                                const key = `${dia}-${slot.id}`;
                                const materia = horario[key];
                                const isWeekend = dia === 'Sábado' || dia === 'Domingo';
                                if (slot.type === 'break' && !isWeekend) return <div key={key} className="grid-cell break-cell"><span>RECREO</span></div>;
                                return (
                                    <div key={key} className={`grid-cell ${materia ? 'filled' : ''} ${isWeekend ? 'weekend-bg' : ''}`}
                                        onDragOver={handleDragOver} onDrop={(e) => handleDrop(e, dia, slot.id, slot.type)}
                                        style={materia ? { backgroundColor: materia.color + '33', borderLeft: `3px solid ${materia.color}` } : {}}
                                    >
                                        {materia && (
                                            <div className="cell-content">
                                                <span className="cell-text">{materia.nombre}</span>
                                                <button className="btn-del" onClick={() => handleRemoveItem(dia, slot.id)}><X size={12}/></button>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </React.Fragment>
                    ))}
                </div>
                
                <div style={{padding: '10px', textAlign: 'center'}}>
                    <button className="btn-add-row" onClick={addNewSlot} style={{display:'inline-flex', alignItems:'center', gap:5, padding: '8px 15px'}}>
                        <Plus size={16}/> Agregar Fila de Hora Extra
                    </button>
                </div>
            </div>
        </main>
      </div>

      <footer className="footer-bar">
        <Link to="/menu"><button className="btn-volver">Volver al menú principal</button></Link>
      </footer>
    </div>
  );
};

export default CalendariosHorarios;