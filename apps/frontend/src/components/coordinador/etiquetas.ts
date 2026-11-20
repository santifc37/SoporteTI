
import type { EstadoSolicitud } from '../../types/solicitud'

export const ESTADOS: { valor: EstadoSolicitud; nombre: string }[] = [
  { valor: 'registrado', nombre: 'Registrado' },
  { valor: 'en_evaluacion', nombre: 'En evaluación' },
  { valor: 'asignado', nombre: 'Asignado' },
  { valor: 'en_atencion', nombre: 'En atención' },
  { valor: 'en_espera', nombre: 'En espera' },
  { valor: 'resuelto', nombre: 'Resuelto' },
  { valor: 'cerrado', nombre: 'Cerrado' },
]

export const NOMBRES_ESTADO: Record<string, string> = Object.fromEntries(
  ESTADOS.map((estado) => [estado.valor, estado.nombre]),
)

export const ESTILOS_ESTADO: Record<string, string> = {
  registrado: 'bg-panel text-texto-secundario',
  en_evaluacion: 'bg-blue-100 text-blue-800',
  asignado: 'bg-indigo-100 text-indigo-800',
  en_atencion: 'bg-amber-100 text-amber-800',
  en_espera: 'bg-orange-100 text-orange-800',
  resuelto: 'bg-emerald-100 text-emerald-800',
  cerrado: 'bg-slate-200 text-slate-700',
}

export const PRIORIDADES = [
  { valor: 'baja', nombre: 'Baja' },
  { valor: 'media', nombre: 'Media' },
  { valor: 'alta', nombre: 'Alta' },
] as const

export const ESTILOS_PRIORIDAD: Record<string, string> = {
  baja: 'bg-slate-100 text-slate-700',
  media: 'bg-amber-100 text-amber-800',
  alta: 'bg-red-100 text-red-700',
}

export const NOMBRES_ROL: Record<string, string> = {
  solicitante: 'Solicitante',
  tecnico: 'Técnico',
  coordinador: 'Coordinador',
}

export const NOMBRES_TIPO_CIERRE: Record<string, string> = {
  solucion: 'Por solución',
  cancelacion: 'Cancelada por el solicitante',
  administrativo: 'Administrativo',
}

export const NOMBRES_TIPO_CAMBIO: Record<string, string> = {
  creacion: 'Solicitud registrada',
  cambio_estado: 'Cambio de estado',
  cambio_prioridad: 'Cambio de prioridad',
  cambio_categoria: 'Cambio de categoría',
  asignacion: 'Asignación de técnico',
  reasignacion: 'Reasignación de técnico',
  solucion: 'Solución registrada',
  cierre_solucion: 'Cierre por solución',
  cierre_administrativo: 'Cierre administrativo',
  cancelacion: 'Cancelación',
}

/** Clase común de los campos de los formularios (la misma que usa el técnico). */
export const CLASE_CAMPO =
  'w-full rounded-lg border border-panel bg-fondo px-3 py-2 text-sm text-texto outline-none transition focus:border-blue-600 focus:ring-2 focus:ring-blue-100'

/** Clase común de las tarjetas de sección. */
export const CLASE_TARJETA = 'rounded-xl border border-panel bg-tarjeta p-5 shadow-sm'

export function formatearFecha(fecha: string | null | undefined): string {
  if (!fecha) {
    return 'No disponible'
  }

  const valor = new Date(fecha)

  if (Number.isNaN(valor.getTime())) {
    return 'Fecha no disponible'
  }

  return new Intl.DateTimeFormat('es-CO', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(valor)
}

/** Traduce un valor guardado en el historial (estado, prioridad) a texto legible. */
export function textoValor(valor: string | null): string {
  if (!valor) {
    return 'Sin valor'
  }

  return NOMBRES_ESTADO[valor] ?? valor.charAt(0).toUpperCase() + valor.slice(1)
}

export function mensajeDeError(err: unknown, porDefecto: string): string {
  return err instanceof Error ? err.message : porDefecto
}
