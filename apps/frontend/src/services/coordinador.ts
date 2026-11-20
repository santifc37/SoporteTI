
import { api } from './api'

import type { MensajeResponse } from '../types/auth'
import type { SolicitudesPagina, PrioridadSolicitud } from '../types/solicitud'
import type {
  ActualizarUsuarioRequest,
  AdjuntoSolicitud,
  AsignacionHistorial,
  CategoriaRequest,
  CategoriasPagina,
  Categoria,
  CrearUsuarioRequest,
  Estadisticas,
  FiltrosCoordinador,
  FiltrosUsuarios,
  HistorialPagina,
  UsuarioListado,
  UsuariosPagina,
} from '../types/coordinador'

interface CategoriaMensaje {
  mensaje: string
  categoria: Categoria
}

const API_URL = import.meta.env.VITE_API_URL ?? '/api/v1'

// Las fechas del filtro llegan como "AAAA-MM-DD"; el backend espera fecha y hora.
function inicioDelDia(fecha: string): string {
  return `${fecha}T00:00:00`
}

function finDelDia(fecha: string): string {
  return `${fecha}T23:59:59`
}

// ------------------------------ Solicitudes ------------------------------

export async function consultarSolicitudes(
  filtros: FiltrosCoordinador = {},
): Promise<SolicitudesPagina> {
  const parametros = new URLSearchParams()

  const valores: Record<string, string | undefined> = {
    estado: filtros.estado,
    prioridad: filtros.prioridad,
    tipo: filtros.tipo,
    categoria_id: filtros.categoria_id,
    tecnico_id: filtros.tecnico_id,
    solicitante_id: filtros.solicitante_id,
    tipo_cierre: filtros.tipo_cierre,
    busqueda: filtros.busqueda?.trim() || undefined,
    fecha_desde: filtros.fecha_desde
      ? inicioDelDia(filtros.fecha_desde)
      : undefined,
    fecha_hasta: filtros.fecha_hasta
      ? finDelDia(filtros.fecha_hasta)
      : undefined,
  }

  for (const [clave, valor] of Object.entries(valores)) {
    if (valor) {
      parametros.set(clave, valor)
    }
  }

  parametros.set('page', String(filtros.page ?? 1))
  parametros.set('limit', String(filtros.limit ?? 20))

  return api<SolicitudesPagina>(`/requests?${parametros.toString()}`)
}

/** RF-09: pasa una solicitud registrada a evaluación. */
export async function iniciarEvaluacion(
  solicitudId: string,
): Promise<MensajeResponse> {
  return api<MensajeResponse>(`/requests/${solicitudId}/status`, {
    method: 'PATCH',
    datos: { estado: 'en_evaluacion' },
  })
}

/** RF-10: categoría y prioridad. Solo se envían los campos que cambian. */
export async function clasificarSolicitud(
  solicitudId: string,
  datos: {
    categoria_id?: string | null
    prioridad?: PrioridadSolicitud
  },
): Promise<MensajeResponse> {
  return api<MensajeResponse>(`/requests/${solicitudId}`, {
    method: 'PATCH',
    datos,
  })
}

/** RF-11 / RF-12: asigna o reasigna el técnico responsable. */
export async function asignarTecnico(
  solicitudId: string,
  tecnicoId: string,
  observacion: string,
): Promise<MensajeResponse> {
  return api<MensajeResponse>(`/requests/${solicitudId}/assignments`, {
    method: 'POST',
    datos: {
      tecnico_id: tecnicoId,
      ...(observacion.trim() ? { observacion: observacion.trim() } : {}),
    },
  })
}

export async function consultarAsignaciones(
  solicitudId: string,
): Promise<AsignacionHistorial[]> {
  const respuesta = await api<{ data: AsignacionHistorial[] }>(
    `/requests/${solicitudId}/assignments`,
  )

  return respuesta.data
}

/** RF-20: cierre por solución (desde resuelto) o administrativo (desde en evaluación). */
export async function cerrarSolicitud(
  solicitudId: string,
  tipoCierre: 'solucion' | 'administrativo',
  motivo: string,
): Promise<MensajeResponse> {
  return api<MensajeResponse>(`/requests/${solicitudId}/close`, {
    method: 'POST',
    datos: {
      tipo_cierre: tipoCierre,
      ...(motivo.trim() ? { motivo_cierre: motivo.trim() } : {}),
    },
  })
}

/** RF-28: historial de cambios de la solicitud. */
export async function consultarHistorial(
  solicitudId: string,
  page = 1,
  limit = 100,
): Promise<HistorialPagina> {
  return api<HistorialPagina>(
    `/requests/${solicitudId}/history?page=${page}&limit=${limit}`,
  )
}

// ------------------------------ Adjuntos (RF-08) ------------------------------

export async function consultarAdjuntosSolicitud(
  solicitudId: string,
): Promise<AdjuntoSolicitud[]> {
  const respuesta = await api<{ data: AdjuntoSolicitud[] }>(
    `/requests/${solicitudId}/attachments`,
  )

  return respuesta.data
}

/** Descarga el archivo con la cookie de sesión y lo devuelve como Blob. */
export async function descargarAdjunto(adjuntoId: string): Promise<Blob> {
  const respuesta = await fetch(
    `${API_URL}/attachments/${encodeURIComponent(adjuntoId)}/download`,
    { credentials: 'include' },
  )

  if (!respuesta.ok) {
    const contenido = await respuesta.json().catch(() => null)
    throw new Error(
      contenido?.error?.mensaje ?? 'No fue posible descargar el archivo.',
    )
  }

  return respuesta.blob()
}

// ------------------------------ Usuarios (RF-03, RF-04, RF-05) ------------------------------

export async function consultarUsuarios(
  filtros: FiltrosUsuarios = {},
): Promise<UsuariosPagina> {
  const parametros = new URLSearchParams()

  if (filtros.rol) {
    parametros.set('rol', filtros.rol)
  }

  if (filtros.activo !== undefined) {
    parametros.set('activo', String(filtros.activo))
  }

  if (filtros.busqueda?.trim()) {
    parametros.set('busqueda', filtros.busqueda.trim())
  }

  parametros.set('page', String(filtros.page ?? 1))
  parametros.set('limit', String(filtros.limit ?? 20))

  return api<UsuariosPagina>(`/users?${parametros.toString()}`)
}

/** Técnicos activos, para los selectores de asignación y de filtros. */
export async function consultarTecnicosActivos(): Promise<UsuarioListado[]> {
  const respuesta = await consultarUsuarios({
    rol: 'tecnico',
    activo: true,
    limit: 100,
  })

  return respuesta.data
}

export async function crearUsuario(
  datos: CrearUsuarioRequest,
): Promise<MensajeResponse> {
  return api<MensajeResponse>('/users', {
    method: 'POST',
    datos,
  })
}

export async function actualizarUsuario(
  usuarioId: string,
  datos: ActualizarUsuarioRequest,
): Promise<MensajeResponse> {
  return api<MensajeResponse>(`/users/${encodeURIComponent(usuarioId)}`, {
    method: 'PATCH',
    datos,
  })
}

/** RF-04: el coordinador asigna una contraseña temporal. */
export async function restablecerContrasena(
  usuarioId: string,
  contrasenaTemporal: string,
): Promise<MensajeResponse> {
  return api<MensajeResponse>(
    `/users/${encodeURIComponent(usuarioId)}/reset-password`,
    {
      method: 'POST',
      datos: { contrasena_temporal: contrasenaTemporal },
    },
  )
}

// ------------------------------ Categorías ------------------------------

export async function consultarCategorias(
  filtros: {
    activa?: boolean
    busqueda?: string
    page?: number
    limit?: number
  } = {},
): Promise<CategoriasPagina> {
  const parametros = new URLSearchParams()

  if (filtros.activa !== undefined) {
    parametros.set('activa', String(filtros.activa))
  }

  if (filtros.busqueda?.trim()) {
    parametros.set('busqueda', filtros.busqueda.trim())
  }

  parametros.set('page', String(filtros.page ?? 1))
  parametros.set('limit', String(filtros.limit ?? 100))

  return api<CategoriasPagina>(`/categories?${parametros.toString()}`)
}

export async function crearCategoria(
  datos: CategoriaRequest,
): Promise<CategoriaMensaje> {
  return api<CategoriaMensaje>('/categories', {
    method: 'POST',
    datos,
  })
}

export async function actualizarCategoria(
  categoriaId: string,
  datos: CategoriaRequest,
): Promise<CategoriaMensaje> {
  return api<CategoriaMensaje>(`/categories/${encodeURIComponent(categoriaId)}`, {
    method: 'PATCH',
    datos,
  })
}

// ------------------------------ Estadísticas (RF-29) ------------------------------

export async function consultarEstadisticas(
  fechaDesde?: string,
  fechaHasta?: string,
): Promise<Estadisticas> {
  const parametros = new URLSearchParams()

  if (fechaDesde) {
    parametros.set('fecha_desde', inicioDelDia(fechaDesde))
  }

  if (fechaHasta) {
    parametros.set('fecha_hasta', finDelDia(fechaHasta))
  }

  const consulta = parametros.toString()

  return api<Estadisticas>(`/statistics${consulta ? `?${consulta}` : ''}`)
}
