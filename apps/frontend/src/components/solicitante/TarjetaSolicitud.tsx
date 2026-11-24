
import type {
  EstadoSolicitud,
  SolicitudResumen,
} from '../../types/solicitud'

interface TarjetaSolicitudProps {
  solicitud: SolicitudResumen
  onVerConversacion: () => void
  onCancelar: () => void
}

const NOMBRES_ESTADO: Record<EstadoSolicitud, string> = {
  registrado: 'Registrado',
  en_evaluacion: 'En evaluación',
  asignado: 'Asignado',
  en_atencion: 'En atención',
  en_espera: 'En espera',
  resuelto: 'Resuelto',
  cerrado: 'Cerrado',
}

const ESTILOS_ESTADO: Record<EstadoSolicitud, string> = {
  registrado: 'bg-slate-100 text-slate-700',
  en_evaluacion: 'bg-blue-100 text-blue-800',
  asignado: 'bg-indigo-100 text-indigo-800',
  en_atencion: 'bg-amber-100 text-amber-800',
  en_espera: 'bg-orange-100 text-orange-800',
  resuelto: 'bg-emerald-100 text-emerald-800',
  cerrado: 'bg-slate-200 text-slate-700',
}

function formatearFecha(fecha: string): string {
  const valor = new Date(fecha)

  if (Number.isNaN(valor.getTime())) {
    return 'Fecha no disponible'
  }

  return new Intl.DateTimeFormat('es-CO', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(valor)
}

export function TarjetaSolicitud({
  solicitud,
  onVerConversacion,
  onCancelar,
}: TarjetaSolicitudProps) {
  const permiteCancelar =
    solicitud.estado === 'registrado' ||
    solicitud.estado === 'en_evaluacion'

  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-300 hover:shadow-md">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            {solicitud.numero}
          </p>

          <h3 className="mt-1 break-words text-base font-semibold text-slate-900">
            {solicitud.titulo}
          </h3>
        </div>

        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold ${ESTILOS_ESTADO[solicitud.estado]}`}
        >
          {NOMBRES_ESTADO[solicitud.estado]}
        </span>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-slate-100 pt-3 text-sm">
        <p className="text-slate-600">
          <span className="font-medium text-slate-800">Tipo:</span>{' '}
          <span className="capitalize">{solicitud.tipo}</span>
        </p>

        <p className="text-slate-600">
          <span className="font-medium text-slate-800">Prioridad:</span>{' '}
          <span className="capitalize">
            {solicitud.prioridad ?? 'Pendiente'}
          </span>
        </p>

        <p className="text-slate-600">
          <span className="font-medium text-slate-800">Categoría:</span>{' '}
          {solicitud.categoria?.nombre ?? 'Sin categoría'}
        </p>

        <p className="text-slate-500">
          {formatearFecha(solicitud.fecha_creacion)}
        </p>
      </div>

      <div className="mt-4 flex flex-wrap gap-2 border-t border-slate-100 pt-3">
        <button
          type="button"
          onClick={onVerConversacion}
          className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 transition hover:bg-blue-100"
        >
          Ver conversación
        </button>

        {permiteCancelar && (
          <button
            type="button"
            onClick={onCancelar}
            className="rounded-lg border border-red-200 bg-white px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-50"
          >
            Cancelar solicitud
          </button>
        )}
      </div>
    </article>
  )
}
