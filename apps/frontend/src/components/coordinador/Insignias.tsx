
import {
  ESTILOS_ESTADO,
  ESTILOS_PRIORIDAD,
  NOMBRES_ESTADO,
} from './etiquetas'

export function InsigniaEstado({
  estado,
  grande = false,
}: {
  estado: string
  grande?: boolean
}) {
  return (
    <span
      className={`inline-flex rounded-full font-semibold ${
        grande ? 'px-3 py-1.5 text-sm' : 'px-3 py-1 text-xs'
      } ${ESTILOS_ESTADO[estado] ?? 'bg-panel text-texto'}`}
    >
      {NOMBRES_ESTADO[estado] ?? estado}
    </span>
  )
}

export function InsigniaPrioridad({
  prioridad,
}: {
  prioridad: string | null
}) {
  if (!prioridad) {
    return (
      <span className="inline-flex rounded-full border border-dashed border-slate-300 px-3 py-1 text-xs font-semibold text-texto-secundario">
        Sin prioridad
      </span>
    )
  }

  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold capitalize ${
        ESTILOS_PRIORIDAD[prioridad] ?? 'bg-panel text-texto'
      }`}
    >
      {prioridad}
    </span>
  )
}
