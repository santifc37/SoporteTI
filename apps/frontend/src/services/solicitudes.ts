
import { api } from './api'
import type {
  FiltrosSolicitudes,
  SolicitudesPagina,
} from '../types/solicitud'

export async function consultarSolicitudesAsignadas(
  filtros: FiltrosSolicitudes = {},
): Promise<SolicitudesPagina> {
  const parametros = new URLSearchParams()

  if (filtros.estado) {
    parametros.set('estado', filtros.estado)
  }

  if (filtros.prioridad) {
    parametros.set('prioridad', filtros.prioridad)
  }

  if (filtros.tipo) {
    parametros.set('tipo', filtros.tipo)
  }

  if (filtros.busqueda?.trim()) {
    parametros.set('busqueda', filtros.busqueda.trim())
  }

  if (filtros.fecha_desde) {
    parametros.set('fecha_desde', filtros.fecha_desde)
  }

  if (filtros.fecha_hasta) {
    parametros.set('fecha_hasta', filtros.fecha_hasta)
  }

  parametros.set('page', String(filtros.page ?? 1))
  parametros.set('limit', String(filtros.limit ?? 20))

  return api<SolicitudesPagina>(
    `/requests?${parametros.toString()}`,
  )
}
