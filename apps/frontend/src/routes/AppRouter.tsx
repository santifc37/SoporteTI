
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
} from 'react-router-dom'

import { PanelLayout } from '../layouts/PanelLayout'
import { AuthProvider, useAuth } from '../hooks/useAuth'
import { LoginPage } from '../pages/LoginPage'

import { SolicitanteDashboardPage } from '../pages/solicitante/SolicitanteDashboardPage'
import { PerfilSolicitantePage } from '../pages/solicitante/PerfilSolicitantePage'
import { CambiarContrasenaPage } from '../pages/solicitante/CambiarContrasenaPage'

import { SolicitudesAsignadasPage } from '../pages/tecnico/SolicitudesAsignadasPage'
import { DetalleSolicitudTecnicoPage } from '../pages/tecnico/DetalleSolicitudTecnicoPage'

import { BandejaSolicitudesPage } from '../pages/coordinador/BandejaSolicitudesPage'
import { DetalleSolicitudCoordinadorPage } from '../pages/coordinador/DetalleSolicitudCoordinadorPage'
import { UsuariosPage } from '../pages/coordinador/UsuariosPage'
import { CategoriasPage } from '../pages/coordinador/CategoriasPage'
import { EstadisticasPage } from '../pages/coordinador/EstadisticasPage'

import { RutaProtegida } from './RutaProtegida'

function InicioSegunRol() {
  const { usuario } = useAuth()

  if (!usuario) {
    return <Navigate to="/login" replace />
  }

  if (usuario.rol === 'tecnico') {
    return <Navigate to="/tecnico" replace />
  }

  if (usuario.rol === 'solicitante') {
    return <Navigate to="/solicitante" replace />
  }

  return <Navigate to="/coordinador" replace />
}

function PanelCoordinador() {
  const ubicacion = useLocation()

  const titulos: Record<string, string> = {
    '/coordinador': 'Bandeja de solicitudes',
    '/coordinador/usuarios': 'Usuarios',
    '/coordinador/categorias': 'Categorías',
    '/coordinador/estadisticas': 'Estadísticas',
    '/coordinador/perfil': 'Mi perfil',
    '/coordinador/cambiar-contrasena': 'Cambiar contraseña',
  }

  const esDetalle = ubicacion.pathname.startsWith('/coordinador/solicitud/')

  return (
    <PanelLayout
      titulo={
        esDetalle
          ? 'Gestión de solicitud'
          : titulos[ubicacion.pathname] ?? 'Panel del coordinador'
      }
      navegacion={[
        { nombre: 'Solicitudes', ruta: '/coordinador' },
        { nombre: 'Usuarios', ruta: '/coordinador/usuarios' },
        { nombre: 'Categorías', ruta: '/coordinador/categorias' },
        { nombre: 'Estadísticas', ruta: '/coordinador/estadisticas' },
        { nombre: 'Mi perfil', ruta: '/coordinador/perfil' },
        { nombre: 'Cambiar contraseña', ruta: '/coordinador/cambiar-contrasena' },
      ]}
    >
      <Routes>
        <Route index element={<BandejaSolicitudesPage />} />
        <Route
          path="solicitud/:solicitudId"
          element={<DetalleSolicitudCoordinadorPage />}
        />
        <Route path="usuarios" element={<UsuariosPage />} />
        <Route path="categorias" element={<CategoriasPage />} />
        <Route path="estadisticas" element={<EstadisticasPage />} />
        <Route path="perfil" element={<PerfilSolicitantePage />} />
        <Route
          path="cambiar-contrasena"
          element={<CambiarContrasenaPage />}
        />
      </Routes>
    </PanelLayout>
  )
}

function PanelTecnico() {
  const ubicacion = useLocation()

  const titulos: Record<string, string> = {
    '/tecnico': 'Solicitudes asignadas',
  }

  const esDetalle = ubicacion.pathname.startsWith('/tecnico/')

  return (
    <PanelLayout
      titulo={
        esDetalle
          ? 'Detalle de solicitud'
          : titulos[ubicacion.pathname] ?? 'Panel del técnico'
      }
      navegacion={[
        {
          nombre: 'Solicitudes asignadas',
          ruta: '/tecnico',
        },
      ]}
    >
      <Routes>
        <Route index element={<SolicitudesAsignadasPage />} />
        <Route
          path="solicitud/:solicitudId"
          element={<DetalleSolicitudTecnicoPage />}
        />
      </Routes>
    </PanelLayout>
  )
}

function PanelSolicitante() {
  const ubicacion = useLocation()

  const titulos: Record<string, string> = {
    '/solicitante': 'Panel del solicitante',
    '/solicitante/perfil': 'Mi perfil',
    '/solicitante/cambiar-contrasena': 'Cambiar contraseña',
  }

  return (
    <PanelLayout
      titulo={titulos[ubicacion.pathname] ?? 'Panel del solicitante'}
      navegacion={[
        {
          nombre: 'Mis casos',
          ruta: '/solicitante',
        },
        {
          nombre: 'Mi perfil',
          ruta: '/solicitante/perfil',
        },
        {
          nombre: 'Cambiar contraseña',
          ruta: '/solicitante/cambiar-contrasena',
        },
      ]}
    >
      <Routes>
        <Route index element={<SolicitanteDashboardPage />} />
        <Route path="perfil" element={<PerfilSolicitantePage />} />
        <Route
          path="cambiar-contrasena"
          element={<CambiarContrasenaPage />}
        />
      </Routes>
    </PanelLayout>
  )
}

function RutasAplicacion() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route element={<RutaProtegida />}>
        <Route path="/" element={<InicioSegunRol />} />

        <Route
          element={<RutaProtegida rolesPermitidos={['tecnico']} />}
        >
          <Route path="/tecnico/*" element={<PanelTecnico />} />
        </Route>

        <Route
          element={<RutaProtegida rolesPermitidos={['solicitante']} />}
        >
          <Route path="/solicitante/*" element={<PanelSolicitante />} />
        </Route>
      </Route>

      <Route
        element={<RutaProtegida rolesPermitidos={['coordinador']} />}
      >
        <Route path="/coordinador/*" element={<PanelCoordinador />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <RutasAplicacion />
      </AuthProvider>
    </BrowserRouter>
  )
}
