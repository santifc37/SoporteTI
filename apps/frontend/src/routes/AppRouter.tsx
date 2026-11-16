import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import { PanelLayout } from '../layouts/PanelLayout'
import { AuthProvider, useAuth } from '../hooks/useAuth'
import { LoginPage } from '../pages/LoginPage'
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
    solicitante: {
      titulo: 'Panel del solicitante',
      ruta: '/solicitante',
    },
    coordinador: {
      titulo: 'Panel del coordinador',
      ruta: '/coordinador',
    },
  }

  if (!rol) {
    return null
  }

  const panel = configuracion[rol]

  return (
    <PanelLayout
      titulo={panel.titulo}
      navegacion={[
        {
          nombre: 'Inicio',
          ruta: panel.ruta,
        },
      ]}
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



function RutasAplicacion() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route element={<RutaProtegida />}>
        <Route path="/" element={<InicioSegunRol />} />

        <Route
          element={
            <RutaProtegida rolesPermitidos={['tecnico']} />
          }
        >
          <Route path="/tecnico/*" element={<ModuloPendiente />} />
        </Route>

        <Route
          element={
            <RutaProtegida rolesPermitidos={['solicitante']} />
          }
        >
          <Route path="/solicitante/*" element={<ModuloPendiente />} />
        </Route>
      </Route>

         <Route element={<RutaProtegida rolesPermitidos={['coordinador']} />}>
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