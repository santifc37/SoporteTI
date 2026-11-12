
export type EstadoSolicitud =
  | 'registrado'
  | 'en_evaluacion'
  | 'asignado'
  | 'en_atencion'
  | 'en_espera'
  | 'resuelto'
  | 'cerrado'

export type PrioridadSolicitud = 'baja' | 'media' | 'alta'

export type TipoSolicitud = 'incidente' | 'requerimiento'

export interface CategoriaResumen {
  id: string
  nombre: string
}

export interface UsuarioResumen {
  id: string
  nombre: string
}

export interface SolicitudResumen {
  id: string
  numero: string
  titulo: string
  tipo: TipoSolicitud
  prioridad: PrioridadSolicitud | null
  estado: EstadoSolicitud
  categoria: CategoriaResumen | null
  solicitante: UsuarioResumen
  tecnico_asignado: UsuarioResumen | null
  fecha_creacion: string
}

export interface PaginacionSolicitudes {
  page: number
  limit: number
  total: number
  total_pages: number
}

export interface SolicitudesPagina {
  data: SolicitudResumen[]
  pagination: PaginacionSolicitudes
}

export interface FiltrosSolicitudes {
  estado?: EstadoSolicitud
  prioridad?: PrioridadSolicitud
  tipo?: TipoSolicitud
  busqueda?: string
  fecha_desde?: string
  fecha_hasta?: string
  page?: number
  limit?: number
}
