
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
    <div className="flex min-h-screen flex-col bg-fondo md:flex-row">
      <aside className="flex w-full shrink-0 flex-col bg-primario p-4 text-white md:sticky md:top-0 md:h-screen md:w-64 md:overflow-y-auto md:p-5">
        <div className="mb-5 md:mb-10">
          <h1 className="text-2xl font-bold">SoporteTI</h1>
          <p className="mt-1 text-sm text-slate-300">
            Gestión de soporte técnico
          </p>
        </div>

        <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-300">
          Navegación
        </p>

        <nav className="flex flex-wrap gap-2 md:flex-1 md:flex-col">
          {navegacion.map((elemento) => (
            <NavLink
              key={elemento.ruta}
              to={elemento.ruta}
              className={({ isActive }) =>
                `rounded-lg px-4 py-3 text-sm font-medium transition ${
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

        <div className="mt-5 border-t border-white/20 pt-4 md:mt-auto">
          <p className="break-words text-sm font-semibold">
            {usuario?.nombre} {usuario?.apellido}
          </p>
          <p className="mb-3 text-xs capitalize text-slate-300">
            {usuario?.rol}
          </p>

          <button
            type="button"
            onClick={manejarCierreSesion}
            className="w-full rounded-lg border border-white/30 px-4 py-2.5 text-sm font-medium transition hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
          >
            Cerrar sesión
          </button>
        </div>
      </aside>

      <div className="min-w-0 flex-1">
        <header className="border-b border-panel bg-tarjeta px-4 py-4 sm:px-6 md:px-8 md:py-5">
          <h2 className="text-xl font-bold text-texto">{titulo}</h2>
        </header>

        <main className="min-w-0 p-4 sm:p-6 md:p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
