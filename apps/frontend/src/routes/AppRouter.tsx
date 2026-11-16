
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

function ModuloPendiente() {
  const { usuario } = useAuth()
  const rol = usuario?.rol

  const configuracion = {
    tecnico: {
      titulo: 'Panel del técnico',
      ruta: '/tecnico',
    },
    coordinador: {
      titulo: 'Panel del coordinador',
      ruta: '/coordinador',
    },
  }

  if (!rol || rol === 'solicitante') {
    return null
  }

  const panel = configuracion[rol]

  return (
    <PanelLayout
      titulo={panel.titulo}
      navegacion={[{ nombre: 'Inicio', ruta: panel.ruta }]}
    >
      <section className="rounded-xl border border-panel bg-tarjeta p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-texto">
          Bienvenido a SoporteTI
        </h2>
        <p className="mt-2 text-sm text-texto-secundario">
          Aquí encontrarás las herramientas correspondientes a tu módulo.
        </p>
      </section>
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
          <Route path="/tecnico/*" element={<ModuloPendiente />} />
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
        <Route path="/coordinador/*" element={<ModuloPendiente />} />
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
