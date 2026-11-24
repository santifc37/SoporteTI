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

  const nombreCompleto =
    `${usuario?.nombre ?? ''} ${usuario?.apellido ?? ''}`.trim()

  const iniciales = nombreCompleto
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((parte) => parte[0].toUpperCase())
    .join('')

  return (
    <div className="flex min-h-screen flex-col bg-fondo lg:flex-row">
      {/* Navegación lateral */}
      <aside className="flex w-full shrink-0 flex-col bg-primario text-white lg:sticky lg:top-0 lg:h-screen lg:w-72">
        <div className="border-b border-white/10 px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/10 text-xl font-bold">
              S
            </div>

            <div>
              <h1 className="text-xl font-bold tracking-tight">
                SoporteTI
              </h1>
              <p className="text-xs text-blue-200">
                Gestión de soporte técnico
              </p>
            </div>
          </div>
        </div>

        <div className="px-5 pt-6">
          <p className="mb-3 px-3 text-[11px] font-bold uppercase tracking-[0.16em] text-blue-200/70">
            Menú principal
          </p>

          <nav className="flex gap-2 overflow-x-auto pb-3 lg:flex-col lg:overflow-visible">
            {navegacion.map((elemento) => (
              <NavLink
                key={elemento.ruta}
                to={elemento.ruta}
                end
                className={({ isActive }) =>
                  `flex shrink-0 items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-white text-primario shadow-lg shadow-black/10'
                      : 'text-blue-100 hover:bg-white/10 hover:text-white'
                  }`
                }
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-current/10 text-xs font-bold">
                  {elemento.nombre.charAt(0).toUpperCase()}
                </span>

                {elemento.nombre}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="mt-auto hidden border-t border-white/10 p-5 lg:block">
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-400/20 text-sm font-bold text-white">
              {iniciales || 'U'}
            </div>

            <div className="min-w-0">
              <p className="truncate text-sm font-semibold">
                {nombreCompleto || 'Usuario'}
              </p>
              <p className="mt-0.5 text-xs capitalize text-blue-200">
                {usuario?.rol}
              </p>
            </div>
          </div>

          <button
            onClick={manejarCierreSesion}
            className="w-full rounded-xl border border-white/20 px-4 py-2.5 text-sm font-medium text-blue-100 transition hover:border-white/40 hover:bg-white/10 hover:text-white"
          >
            Cerrar sesión
          </button>
        </div>
      </aside>

      {/* Contenido */}
      <div className="flex min-h-screen min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex min-h-[76px] items-center justify-between border-b border-slate-200/80 bg-white/90 px-5 py-4 backdrop-blur-md sm:px-8">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-texto-secundario">
              SoporteTI / Panel
            </p>
            <h2 className="mt-1 text-lg font-bold text-texto sm:text-xl">
              {titulo}
            </h2>
          </div>

          <div className="hidden items-center gap-3 sm:flex">
            <div className="text-right">
              <p className="text-sm font-semibold text-texto">
                {nombreCompleto || 'Usuario'}
              </p>
              <p className="text-xs capitalize text-texto-secundario">
                {usuario?.rol}
              </p>
            </div>

            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-primario">
              {iniciales || 'U'}
            </div>
          </div>
        </header>

        <main className="animacion-aparecer flex-1 p-5 sm:p-8 lg:p-9">
          <div className="mx-auto w-full max-w-[1500px]">
            {children}
          </div>
        </main>

        {/* Cierre de sesión visible en móvil */}
        <div className="border-t border-slate-200 bg-white px-5 py-4 lg:hidden">
          <div className="flex items-center justify-between gap-3">
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-texto">
                {nombreCompleto || 'Usuario'}
              </p>
              <p className="text-xs capitalize text-texto-secundario">
                {usuario?.rol}
              </p>
            </div>

            <button
              onClick={manejarCierreSesion}
              className="shrink-0 rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold text-texto transition hover:bg-slate-100"
            >
              Cerrar sesión
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}