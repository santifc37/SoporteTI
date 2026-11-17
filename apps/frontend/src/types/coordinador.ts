
import type { MedioContacto, RolUsuario } from './auth'
import type {
  EstadoSolicitud,
  FiltrosSolicitudes,
  PaginacionSolicitudes,
  PrioridadSolicitud,
} from './solicitud'

export type TipoCierre = 'solucion' | 'cancelacion' | 'administrativo'

export interface FiltrosCoordinador extends FiltrosSolicitudes {
  categoria_id?: string
  tecnico_id?: string
  solicitante_id?: string
  tipo_cierre?: TipoCierre
}

// ------------------------------ Usuarios (RF-03, RF-04, RF-05) ------------------------------

export interface UsuarioListado {
  id: string
  nombre: string
  apellido: string
  correo: string
  rol: RolUsuario
  activo: boolean
  medio_contacto_preferido: MedioContacto
  telefono: string | null
  fecha_creacion: string
}

export interface UsuariosPagina {
  data: UsuarioListado[]
  pagination: PaginacionSolicitudes
}

export interface FiltrosUsuarios {
  rol?: RolUsuario
  activo?: boolean
  busqueda?: string
  page?: number
  limit?: number
}

export interface CrearUsuarioRequest {
  nombre: string
  apellido: string
  correo: string
  contrasena: string
  rol: RolUsuario
  medio_contacto_preferido: MedioContacto
  telefono?: string | null
}

export interface ActualizarUsuarioRequest {
  nombre?: string
  apellido?: string
  correo?: string
  telefono?: string | null
  medio_contacto_preferido?: MedioContacto
  rol?: RolUsuario
  activo?: boolean
}

// ------------------------------ Categorías ------------------------------

export interface Categoria {
  id: string
  nombre: string
  descripcion: string | null
  activa: boolean
}

export interface CategoriasPagina {
  data: Categoria[]
  pagination: PaginacionSolicitudes
}

export interface CategoriaRequest {
  nombre?: string
  descripcion?: string | null
  activa?: boolean
}

// ------------------------------ Asignaciones (RF-11, RF-12) ------------------------------

export interface AsignacionHistorial {
  id: string
  tecnico_id: string
  tecnico_nombre: string
  asignado_por: string | null
  fecha_asignacion: string
  fecha_finalizacion: string | null
  observacion: string | null
}

// ------------------------------ Historial de cambios (RF-28) ------------------------------

export interface CambioHistorial {
  id: string
  solicitud_id: string
  usuario: {
    id: string
    nombre: string
    rol: string
  }
  tipo_cambio: string
  valor_anterior: string | null
  valor_nuevo: string | null
  observacion: string | null
  fecha_cambio: string
}

export interface HistorialPagina {
  data: CambioHistorial[]
  pagination: PaginacionSolicitudes
}

// ------------------------------ Adjuntos de la solicitud (RF-08) ------------------------------

export interface AdjuntoSolicitud {
  id: string
  nombre_archivo: string
  tipo_archivo: string
  tamano: number
  subido_por: string
  fecha_subida: string
}

// ------------------------------ Estadísticas (RF-29) ------------------------------

export interface Estadisticas {
  total_solicitudes: number
  por_estado: Record<EstadoSolicitud, number>
  por_prioridad: Record<PrioridadSolicitud, number>
  sin_prioridad: number
  por_categoria: {
    categoria_id: string
    nombre: string
    cantidad: number
  }[]
  sin_categoria: number
  por_tecnico: {
    tecnico_id: string
    nombre: string
    cantidad: number
  }[]
  sin_asignar: number
  tiempo_promedio_atencion: number | null
  solicitudes_con_tiempo: number
}
