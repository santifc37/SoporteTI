
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
    </section>
  )
}
