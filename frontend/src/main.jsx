import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import './index.css';
import App from './App.jsx';

// Importaciones de tus páginas
import HomePage from './pages/Pagina_Home/pagina_home.jsx';
import RegisterPage from './pages/Pagina_Registro/pagina_registro.jsx';
import LoginPage from './pages/Pagina_Login/pagina_login.jsx';
import MenuPage from './pages/Pagina_Menu/pagina_menu.jsx';
import Pagina_Materias from './pages/Paginas_Portal/pagina_materias.jsx';
import Pagina_Horario from './pages/Pagina_Horario/pagina_horario.jsx'; // Nota: En tu estructura anterior se llamaba CalendariosHorarios
import Pagina_Resenas from './pages/Pagina_Resenas/pagina_resenas.jsx';
import Pagina_Analisis from './pages/Pagina_Analisis/pagina_analisis.jsx';
import Pagina_Asistente from './pages/Pagina_Asistente/pagina_asistente.jsx';
import Pagina_Subir from './pages/Pagina_subir/pagina_subir.jsx';
import AgregarResena from './pages/Pagina_agregar_resena/agregar_resena.jsx';
import CalendarioIPN from './pages/Pagina_calendario/pagina_calendarioipn.jsx'; 
import ResetPasswordPage from './pages/Pagina_reset/pagina_reset_password.jsx';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'registro',
        element: <RegisterPage />,
      },
      {
        path: 'login',
        element: <LoginPage />,
      },
      {
        path: 'menu',
        element: <MenuPage />,
      },
      {
        path: 'portal',
        element: <Pagina_Materias />,
      },
      {
        path: 'horarios',
        element: <Pagina_Horario />,
      },
      {
        path: 'resenas',
        element: <Pagina_Resenas />,
      },      
      {
        path: 'analisis',
        element: <Pagina_Analisis />,
      },
      {
        path: 'asistente',
        element: <Pagina_Asistente />,
      },
      {
        path: 'subir-recurso',
        element: <Pagina_Subir />,
      },
      {
        path: 'agregar-resena',
        element: <AgregarResena />,
      },
      {
        path: 'calendario',
        element: <CalendarioIPN />,
      },
      {
        path: 'reset-password',
        element: <ResetPasswordPage />,
      },
    ],
  },
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);