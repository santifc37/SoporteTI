
import { useEffect, useState, type FormEvent } from 'react'

import { Boton } from '../../components/Boton'
import { MensajeEstado } from '../../components/MensajeEstado'
import { useAuth } from '../../hooks/useAuth'
import { actualizarPerfil } from '../../services/usuarios'
import type { MedioContacto } from '../../types/auth'

export function PerfilSolicitantePage() {
  const { usuario, refrescarUsuario } = useAuth()

  const [nombre, setNombre] = useState(usuario?.nombre ?? '')
  const [apellido, setApellido] = useState(usuario?.apellido ?? '')
  const [telefono, setTelefono] = useState(usuario?.telefono ?? '')
  const [medioContacto, setMedioContacto] =
    useState<MedioContacto>(
      usuario?.medio_contacto_preferido ?? 'correo',
    )

  const [guardando, setGuardando] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [tipoMensaje, setTipoMensaje] = useState<'exito' | 'error'>(
    'exito',
  )

  useEffect(() => {
    if (!usuario) return

    setNombre(usuario.nombre)
    setApellido(usuario.apellido)
    setTelefono(usuario.telefono ?? '')
    setMedioContacto(usuario.medio_contacto_preferido ?? 'correo')
  }, [usuario])

  async function guardarCambios(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setMensaje('')

    if (!usuario) {
      setTipoMensaje('error')
      setMensaje('No se encontró la información de tu cuenta.')
      return
    }

    if (medioContacto === 'telefono' && !telefono.trim()) {
      setTipoMensaje('error')
      setMensaje('Debes registrar un teléfono para utilizarlo como medio de contacto.')
      return
    }

    if (!nombre.trim() || !apellido.trim()) {
      setTipoMensaje('error')
      setMensaje('El nombre y el apellido son obligatorios.')
      return
    }

    setGuardando(true)

    try {
      await actualizarPerfil(usuario.id, {
        nombre: nombre.trim(),
        apellido: apellido.trim(),
        telefono: telefono.trim() || null,
        medio_contacto_preferido: medioContacto,
      })

      await refrescarUsuario()

      setTipoMensaje('exito')
      setMensaje('Tus datos de perfil se actualizaron correctamente.')
    } catch (error) {
      setTipoMensaje('error')
      setMensaje(
        error instanceof Error
          ? error.message
          : 'No fue posible actualizar tus datos.',
      )
    } finally {
      setGuardando(false)
    }
  }

  if (!usuario) {
    return (
      <MensajeEstado
        tipo="error"
        mensaje="No se encontró la información de tu cuenta."
      />
    )
  }

  const estiloCampo =
    'mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-800 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100'

  return (
    <section className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Mi perfil
        </h1>

        <p className="mt-1 text-sm text-slate-600">
          Consulta y actualiza tus datos personales y de contacto.
        </p>
      </div>

      <form
        onSubmit={guardarCambios}
        className="space-y-6 rounded-xl border border-slate-200 bg-slate-50 p-5 shadow-sm sm:p-7"
      >
        <div>
          <h2 className="text-base font-semibold text-slate-900">
            Información personal
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Estos datos identifican tu cuenta en el sistema.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <label className="block text-sm font-medium text-slate-700">
            Nombre
            <input
              type="text"
              value={nombre}
              onChange={(evento) => setNombre(evento.target.value)}
              maxLength={100}
              required
              className={estiloCampo}
            />
          </label>

          <label className="block text-sm font-medium text-slate-700">
            Apellido
            <input
              type="text"
              value={apellido}
              onChange={(evento) => setApellido(evento.target.value)}
              maxLength={100}
              required
              className={estiloCampo}
            />
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">
            Correo electrónico
            <input
              type="email"
              value={usuario.correo}
              disabled
              className={`${estiloCampo} cursor-not-allowed bg-slate-100 text-slate-500`}
            />
          </label>

          <p className="mt-1 text-xs text-slate-500">
            El correo no se puede modificar desde el perfil.
          </p>
        </div>

        <div className="border-t border-slate-200 pt-5">
          <h2 className="text-base font-semibold text-slate-900">
            Información de contacto
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Indica cómo prefieres recibir información sobre tus solicitudes.
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">
            Teléfono
            <input
              type="tel"
              value={telefono}
              onChange={(evento) => setTelefono(evento.target.value)}
              maxLength={30}
              placeholder="Ej. 3001234567"
              className={estiloCampo}
            />
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">
            Medio de contacto preferido
            <select
              value={medioContacto}
              onChange={(evento) =>
                setMedioContacto(evento.target.value as MedioContacto)
              }
              className={estiloCampo}
            >
              <option value="correo">Correo electrónico</option>
              <option value="telefono">Teléfono</option>
            </select>
          </label>

          {medioContacto === 'telefono' && (
            <p className="mt-1 text-xs text-slate-500">
              Necesitas registrar un número de teléfono para seleccionar esta opción.
            </p>
          )}
        </div>

        {mensaje && (
          <MensajeEstado tipo={tipoMensaje} mensaje={mensaje} />
        )}

        <div className="flex justify-end border-t border-slate-200 pt-5">
          <Boton type="submit" disabled={guardando}>
            {guardando ? 'Guardando...' : 'Guardar cambios'}
          </Boton>
        </div>
      </form>
    </section>
  )
}
