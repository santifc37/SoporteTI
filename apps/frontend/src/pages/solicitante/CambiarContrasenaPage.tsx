
import { useState, type FormEvent } from 'react'

import { api } from '../../services/api'

export function CambiarContrasenaPage() {
  const [contrasenaActual, setContrasenaActual] = useState('')
  const [contrasenaNueva, setContrasenaNueva] = useState('')
  const [confirmacion, setConfirmacion] = useState('')
  const [guardando, setGuardando] = useState(false)
  const [error, setError] = useState('')
  const [exito, setExito] = useState('')

  async function cambiarContrasena(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    setError('')
    setExito('')

    if (contrasenaNueva.length < 8) {
      setError('La nueva contraseña debe tener al menos 8 caracteres.')
      return
    }

    if (contrasenaNueva.length > 128) {
      setError('La nueva contraseña no puede superar los 128 caracteres.')
      return
    }

    if (contrasenaNueva === contrasenaActual) {
      setError('La nueva contraseña debe ser diferente a la actual.')
      return
    }

    if (contrasenaNueva !== confirmacion) {
      setError('La confirmación no coincide con la nueva contraseña.')
      return
    }

    try {
      setGuardando(true)

      await api<{ mensaje: string }>('/auth/change-password', {
        method: 'POST',
        datos: {
          contrasena_actual: contrasenaActual,
          contrasena_nueva: contrasenaNueva,
        },
      })

      setContrasenaActual('')
      setContrasenaNueva('')
      setConfirmacion('')
      setExito('Tu contraseña fue actualizada correctamente.')
    } catch (err: unknown) {
      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible actualizar la contraseña.',
      )
    } finally {
      setGuardando(false)
    }
  }

  return (
    <section className="mx-auto w-full max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Cambiar contraseña
        </h1>

        <p className="mt-1 text-sm text-slate-600">
          Actualiza la contraseña de acceso a tu cuenta.
        </p>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <form onSubmit={cambiarContrasena} className="space-y-5">
          <div>
            <label
              htmlFor="contrasena-actual"
              className="mb-2 block text-sm font-semibold text-slate-700"
            >
              Contraseña actual
            </label>

            <input
              id="contrasena-actual"
              type="password"
              autoComplete="current-password"
              value={contrasenaActual}
              onChange={(event) => setContrasenaActual(event.target.value)}
              maxLength={128}
              required
              disabled={guardando}
              className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-100"
              placeholder="Ingresa tu contraseña actual"
            />
          </div>

          <div>
            <label
              htmlFor="contrasena-nueva"
              className="mb-2 block text-sm font-semibold text-slate-700"
            >
              Nueva contraseña
            </label>

            <input
              id="contrasena-nueva"
              type="password"
              autoComplete="new-password"
              value={contrasenaNueva}
              onChange={(event) => setContrasenaNueva(event.target.value)}
              minLength={8}
              maxLength={128}
              required
              disabled={guardando}
              className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-100"
              placeholder="Escribe una nueva contraseña"
            />

            <p className="mt-1 text-xs text-slate-500">
              Debe tener entre 8 y 128 caracteres.
            </p>
          </div>

          <div>
            <label
              htmlFor="confirmar-contrasena"
              className="mb-2 block text-sm font-semibold text-slate-700"
            >
              Confirmar nueva contraseña
            </label>

            <input
              id="confirmar-contrasena"
              type="password"
              autoComplete="new-password"
              value={confirmacion}
              onChange={(event) => setConfirmacion(event.target.value)}
              maxLength={128}
              required
              disabled={guardando}
              className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-100"
              placeholder="Repite la nueva contraseña"
            />
          </div>

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {exito && (
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
              {exito}
            </div>
          )}

          <div className="flex justify-end border-t border-slate-100 pt-4">
            <button
              type="submit"
              disabled={
                guardando ||
                !contrasenaActual ||
                !contrasenaNueva ||
                !confirmacion
              }
              className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {guardando ? 'Actualizando...' : 'Actualizar contraseña'}
            </button>
          </div>
        </form>
      </div>
    </section>
  )
}
