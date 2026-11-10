
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
    return <p className="p-6 text-center text-texto">Verificando sesión...</p>
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
      await login({ correo, contrasena })
      const respuesta = await import('../services/auth')
      const sesion = await respuesta.obtenerUsuario()

const ruta =
  sesion.usuario.rol === 'tecnico'
    ? '/tecnico'
    : sesion.usuario.rol === 'solicitante'
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
    <main className="flex min-h-screen items-center justify-center bg-fondo px-4 py-8">
      <section className="w-full max-w-md rounded-2xl border border-panel bg-tarjeta p-8 shadow-xl">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-primario">SoporteTI</h1>
          <p className="mt-2 text-sm text-texto-secundario">
            Sistema de gestión de solicitudes de soporte
          </p>
        </div>

        <form onSubmit={manejarEnvio} className="space-y-5">
          <div>
            <label htmlFor="correo" className="mb-2 block text-sm font-semibold text-texto">
              Correo electrónico
            </label>
            <input
              id="correo"
              type="email"
              value={correo}
              onChange={(evento) => setCorreo(evento.target.value)}
              required
              autoComplete="username"
              className="w-full rounded-lg border border-panel bg-white px-4 py-3 text-texto outline-none transition focus:border-accion focus:ring-2 focus:ring-accion/20"
              placeholder="usuario@correo.com"
            />
          </div>

          <div>
            <label htmlFor="contrasena" className="mb-2 block text-sm font-semibold text-texto">
              Contraseña
            </label>
            <input
              id="contrasena"
              type="password"
              value={contrasena}
              onChange={(evento) => setContrasena(evento.target.value)}
              required
              autoComplete="current-password"
              className="w-full rounded-lg border border-panel bg-white px-4 py-3 text-texto outline-none transition focus:border-accion focus:ring-2 focus:ring-accion/20"
              placeholder="Ingresa tu contraseña"
            />
          </div>

          {error && (
            <p className="rounded-lg border border-error/20 bg-error/10 p-3 text-sm text-error">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={enviando}
            className="w-full rounded-lg bg-primario px-4 py-3 font-semibold text-white transition hover:bg-accion disabled:cursor-not-allowed disabled:opacity-60"
          >
            {enviando ? 'Ingresando...' : 'Iniciar sesión'}
          </button>
        </form>
      </section>
    </main>
  )
}
