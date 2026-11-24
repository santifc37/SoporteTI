
import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export function LoginPage() {
  const { usuario, login, cargando } = useAuth()
  const navigate = useNavigate()

  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  if (cargando) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-fondo">
        <div className="text-center">
          <div className="mx-auto mb-4 h-9 w-9 animate-spin rounded-full border-4 border-blue-100 border-t-accion" />
          <p className="text-sm text-texto-secundario">
            Verificando sesión...
          </p>
        </div>
      </main>
    )
  }

  if (usuario) {
    const ruta =
      usuario.rol === 'tecnico'
        ? '/tecnico'
        : usuario.rol === 'solicitante'
          ? '/solicitante'
          : '/coordinador'

    return <Navigate to={ruta} replace />
  }

  async function manejarEnvio(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError('')
    setEnviando(true)

    try {
      const usuarioAutenticado = await login({
        correo,
        contrasena,
      })

      const ruta =
        usuarioAutenticado.rol === 'tecnico'
          ? '/tecnico'
          : usuarioAutenticado.rol === 'solicitante'
            ? '/solicitante'
            : '/coordinador'

      navigate(ruta, { replace: true })
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'No fue posible iniciar sesión.',
      )
    } finally {
      setEnviando(false)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-fondo px-5 py-10">
      <section className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-7 shadow-sm sm:p-9">
        <header className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-primario text-2xl font-bold text-white">
            S
          </div>

          <h1 className="text-2xl font-bold text-primario">
            SoporteTI
          </h1>

          <p className="mt-2 text-sm text-texto-secundario">
            Inicio de sesión
          </p>
        </header>

        <form onSubmit={manejarEnvio} className="space-y-5">
          <div>
            <label
              htmlFor="correo"
              className="mb-2 block text-sm font-semibold text-texto"
            >
              Correo electrónico
            </label>

            <input
              id="correo"
              type="email"
              value={correo}
              onChange={(evento) => setCorreo(evento.target.value)}
              required
              autoComplete="username"
              placeholder="usuario@correo.com"
              className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-texto outline-none transition placeholder:text-slate-400 focus:border-accion focus:ring-2 focus:ring-blue-100"
            />
          </div>

          <div>
            <label
              htmlFor="contrasena"
              className="mb-2 block text-sm font-semibold text-texto"
            >
              Contraseña
            </label>

            <input
              id="contrasena"
              type="password"
              value={contrasena}
              onChange={(evento) => setContrasena(evento.target.value)}
              required
              autoComplete="current-password"
              placeholder="Ingresa tu contraseña"
              className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-texto outline-none transition placeholder:text-slate-400 focus:border-accion focus:ring-2 focus:ring-blue-100"
            />
          </div>

          {error && (
            <div
              role="alert"
              className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={enviando}
            className="w-full rounded-lg bg-primario px-4 py-3 text-sm font-semibold text-white transition hover:bg-accion disabled:cursor-not-allowed disabled:opacity-60"
          >
            {enviando ? 'Ingresando...' : 'Iniciar sesión'}
          </button>
        </form>

        <footer className="mt-8 border-t border-slate-100 pt-5 text-center">
          <p className="text-xs text-texto-secundario">
            Sistema de gestión de soporte técnico
          </p>
        </footer>
      </section>
    </main>
  )
}
