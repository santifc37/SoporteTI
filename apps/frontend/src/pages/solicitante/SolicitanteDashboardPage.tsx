
import { useEffect, useMemo, useState } from 'react'

import { Boton } from '../../components/Boton'
import { Cargando } from '../../components/Cargando'
import { ConversacionSolicitud } from '../../components/solicitante/ConversacionSolicitud'
import { FormularioNuevaSolicitud } from '../../components/solicitante/FormularioNuevaSolicitud'
import { TarjetaSolicitud } from '../../components/solicitante/TarjetaSolicitud'
import { MensajeEstado } from '../../components/MensajeEstado'
import { api } from '../../services/api'

import type {
  PrioridadSolicitud,
  SolicitudResumen,
  SolicitudesPagina,
} from '../../types/solicitud'

const PRIORIDAD_ORDEN: Record<PrioridadSolicitud, number> = {
  alta: 0,
  media: 1,
  baja: 2,
}

function ordenarSolicitudes(solicitudes: SolicitudResumen[]) {
  return [...solicitudes].sort((a, b) => {
    const aCerrada = a.estado === 'cerrado' || a.estado === 'resuelto'
    const bCerrada = b.estado === 'cerrado' || b.estado === 'resuelto'

    if (aCerrada !== bCerrada) {
      return Number(aCerrada) - Number(bCerrada)
    }

    const prioridadA = a.prioridad ? PRIORIDAD_ORDEN[a.prioridad] : 3
    const prioridadB = b.prioridad ? PRIORIDAD_ORDEN[b.prioridad] : 3

    if (prioridadA !== prioridadB) {
      return prioridadA - prioridadB
    }

    return (
      new Date(b.fecha_creacion).getTime() -
      new Date(a.fecha_creacion).getTime()
    )
  })
}

export function SolicitanteDashboardPage() {
  const [resultado, setResultado] = useState<SolicitudesPagina | null>(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [mostrarFormulario, setMostrarFormulario] = useState(false)

  const [solicitudConversacion, setSolicitudConversacion] =
    useState<SolicitudResumen | null>(null)

  const [solicitudCancelar, setSolicitudCancelar] =
    useState<SolicitudResumen | null>(null)

  const [motivoCancelacion, setMotivoCancelacion] = useState('')
  const [cancelando, setCancelando] = useState(false)
  const [errorCancelacion, setErrorCancelacion] = useState('')

  const [recarga, setRecarga] = useState(0)
  const [mensajeExito, setMensajeExito] = useState('')

  useEffect(() => {
    let vigente = true

    setCargando(true)

    api<SolicitudesPagina>('/requests?page=1&limit=100')
      .then((respuesta) => {
        if (!vigente) return

        setResultado(respuesta)
        setError('')
      })
      .catch((err: unknown) => {
        if (!vigente) return

        setError(
          err instanceof Error
            ? err.message
            : 'No fue posible consultar tus solicitudes.',
        )
      })
      .finally(() => {
        if (vigente) setCargando(false)
      })

    return () => {
      vigente = false
    }
  }, [recarga])

  const solicitudesOrdenadas = useMemo(
    () => ordenarSolicitudes(resultado?.data ?? []),
    [resultado],
  )

  function solicitudCreada() {
    setMostrarFormulario(false)
    setMensajeExito('Tu solicitud fue registrada correctamente.')
    setRecarga((actual) => actual + 1)
  }

  function abrirCancelacion(solicitud: SolicitudResumen) {
    setSolicitudCancelar(solicitud)
    setMotivoCancelacion('')
    setErrorCancelacion('')
  }

  function cerrarCancelacion() {
    if (cancelando) return

    setSolicitudCancelar(null)
    setMotivoCancelacion('')
    setErrorCancelacion('')
  }

  async function confirmarCancelacion(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!solicitudCancelar) return

    const motivo = motivoCancelacion.trim()

    if (!motivo) {
      setErrorCancelacion('Debes escribir el motivo de la cancelación.')
      return
    }

    if (motivo.length > 1000) {
      setErrorCancelacion('El motivo no puede superar los 1000 caracteres.')
      return
    }

    try {
      setCancelando(true)
      setErrorCancelacion('')

      await api<unknown>(
        `/requests/${solicitudCancelar.id}/cancel`,
        {
          method: 'POST',
          datos: { motivo },
        },
      )

      setSolicitudCancelar(null)
      setMotivoCancelacion('')
      setMensajeExito('La solicitud fue cancelada correctamente.')
      setRecarga((actual) => actual + 1)
    } catch (err: unknown) {
      setErrorCancelacion(
        err instanceof Error
          ? err.message
          : 'No fue posible cancelar la solicitud.',
      )
    } finally {
      setCancelando(false)
    }
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Mis casos</h1>

          <p className="mt-1 text-sm text-slate-600">
            Consulta el estado de tus solicitudes de soporte.
          </p>
        </div>

        <Boton
          onClick={() => {
            setMensajeExito('')
            setMostrarFormulario(true)
          }}
        >
          + Nueva solicitud
        </Boton>
      </div>

      {mensajeExito && (
        <div className="rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800">
          {mensajeExito}
        </div>
      )}

      {error && <MensajeEstado tipo="error" mensaje={error} />}

      {cargando ? (
        <Cargando mensaje="Consultando tus solicitudes..." />
      ) : solicitudesOrdenadas.length > 0 ? (
        <div className="space-y-4">
          {solicitudesOrdenadas.map((solicitud) => (
            <TarjetaSolicitud
              key={solicitud.id}
              solicitud={solicitud}
              onVerConversacion={() => setSolicitudConversacion(solicitud)}
              onCancelar={() => abrirCancelacion(solicitud)}
            />
          ))}
        </div>
      ) : (
        !error && (
          <div className="rounded-xl border border-slate-200 bg-white px-6 py-12 text-center shadow-sm">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-500">
              <span className="text-xl">+</span>
            </div>

            <h2 className="mt-4 text-lg font-semibold text-slate-900">
              Todavía no tienes casos registrados
            </h2>

            <p className="mt-2 text-sm text-slate-600">
              Cuando registres una solicitud, podrás consultar aquí su estado
              y seguimiento.
            </p>

            <div className="mt-5">
              <Boton
                onClick={() => {
                  setMensajeExito('')
                  setMostrarFormulario(true)
                }}
              >
                Crear mi primera solicitud
              </Boton>
            </div>
          </div>
        )
      )}

      {mostrarFormulario && (
        <FormularioNuevaSolicitud
          onCerrar={() => setMostrarFormulario(false)}
          onCreada={solicitudCreada}
        />
      )}

      {solicitudConversacion && (
        <ConversacionSolicitud
          solicitud={solicitudConversacion}
          onCerrar={() => setSolicitudConversacion(null)}
        />
      )}

      {solicitudCancelar && (
        <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-950/50 p-4">
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="titulo-cancelacion"
            className="my-auto w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2
                  id="titulo-cancelacion"
                  className="text-xl font-bold text-slate-900"
                >
                  Cancelar solicitud
                </h2>

                <p className="mt-1 text-sm text-slate-600">
                  Estás a punto de cancelar el caso{' '}
                  <span className="font-semibold text-slate-800">
                    {solicitudCancelar.numero}
                  </span>
                  .
                </p>
              </div>

              <button
                type="button"
                onClick={cerrarCancelacion}
                disabled={cancelando}
                aria-label="Cerrar"
                className="rounded-lg px-2 py-1 text-xl text-slate-500 hover:bg-slate-100 disabled:opacity-50"
              >
                ×
              </button>
            </div>

            <form onSubmit={confirmarCancelacion} className="mt-5 space-y-4">
              <div>
                <label
                  htmlFor="motivo-cancelacion"
                  className="mb-2 block text-sm font-semibold text-slate-700"
                >
                  Motivo de la cancelación
                </label>

                <textarea
                  id="motivo-cancelacion"
                  value={motivoCancelacion}
                  onChange={(event) => setMotivoCancelacion(event.target.value)}
                  placeholder="Explica por qué deseas cancelar esta solicitud..."
                  rows={4}
                  maxLength={1000}
                  required
                  disabled={cancelando}
                  className="w-full resize-y rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-100"
                />

                <p className="mt-1 text-right text-xs text-slate-500">
                  {motivoCancelacion.length}/1000 caracteres
                </p>
              </div>

              {errorCancelacion && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  {errorCancelacion}
                </div>
              )}

              <div className="rounded-lg bg-amber-50 px-3 py-3 text-sm text-amber-800">
                Esta acción cambiará el estado de la solicitud a cerrado.
                Deberás crear una nueva solicitud si necesitas asistencia
                posteriormente.
              </div>

              <div className="flex flex-col-reverse justify-end gap-2 sm:flex-row">
                <button
                  type="button"
                  onClick={cerrarCancelacion}
                  disabled={cancelando}
                  className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Volver
                </button>

                <button
                  type="submit"
                  disabled={cancelando || !motivoCancelacion.trim()}
                  className="rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {cancelando ? 'Cancelando...' : 'Confirmar cancelación'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  )
}
