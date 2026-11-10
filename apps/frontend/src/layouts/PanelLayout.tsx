
import { NavLink, useNavigate } from 'react-router-dom'
import type { ReactNode } from 'react'
import { useAuth } from '../hooks/useAuth'

interface ElementoNavegacion {
  nombre: string
  ruta: string
}

interface PanelLayoutProps {
  titulo: string
  navegacion: ElementoNavegacion[]
  children: ReactNode
}

export function PanelLayout({
  titulo,
  navegacion,
  children,
}: PanelLayoutProps) {
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()

  async function manejarCierreSesion() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="flex min-h-screen bg-fondo">
      <aside className="flex w-64 flex-col bg-primario p-5 text-white">
        <div className="mb-10">
          <h1 className="text-2xl font-bold">SoporteTI</h1>
          <p className="mt-1 text-sm text-slate-300">
            Gestión de soporte técnico
          </p>
        </div>

        <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-300">
          Navegación
        </p>

        <nav className="flex-1 space-y-2">
          {navegacion.map((elemento) => (
            <NavLink
              key={elemento.ruta}
              to={elemento.ruta}
              className={({ isActive }) =>
                `block rounded-lg px-4 py-3 text-sm font-medium transition ${
                  isActive
                    ? 'bg-accion text-white'
                    : 'text-slate-200 hover:bg-white/10'
                }`
              }
            >
              {elemento.nombre}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/20 pt-4">
          <p className="text-sm font-semibold">
            {usuario?.nombre} {usuario?.apellido}
          </p>
          <p className="mb-4 text-xs capitalize text-slate-300">
            {usuario?.rol}
          </p>

          <button
            onClick={manejarCierreSesion}
            className="w-full rounded-lg border border-white/30 px-4 py-2 text-sm transition hover:bg-white/10"
          >
            Cerrar sesión
          </button>
        </div>
      </aside>

      <div className="min-w-0 flex-1">
        <header className="border-b border-panel bg-tarjeta px-8 py-5">
          <h2 className="text-xl font-bold text-texto">{titulo}</h2>
        </header>

        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
