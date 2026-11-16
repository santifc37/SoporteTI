
import { api } from './api'

import type {
  EstadoSolicitud,
  PrioridadSolicitud,
  TipoSolicitud,
  CategoriaResumen,
  UsuarioResumen,
} from '../types/solicitud'

export interface SolicitudDetalle {
  id: string
  numero: string
  titulo: string
  descripcion: string
  tipo: TipoSolicitud
  prioridad: PrioridadSolicitud | null
  estado: EstadoSolicitud
  ubicacion: string
  placa_equipo: string | null
  medio_contacto: string
  dato_contacto: string
  solicitante: UsuarioResumen
  categoria: CategoriaResumen | null
  tecnico_asignado: UsuarioResumen | null
  solucion_final: string | null
  resuelto_por: string | null
  fecha_resolucion: string | null
  tipo_cierre: 'solucion' | 'cancelacion' | 'administrativo' | null
  motivo_cierre: string | null
  fecha_creacion: string
  fecha_actualizacion: string
  fecha_cierre: string | null
}

export interface Intervencion {
  id: string
  solicitud_id: string
  tecnico_id: string
  tecnico_nombre?: string
  descripcion: string
  diagnostico: string | null
  visibilidad: 'interna' | 'solicitante'
  fecha_registro: string
}

export interface IntervencionesRespuesta {
  data: Intervencion[]
}

export interface RespuestaOperacion {
  mensaje: string
  solicitud?: {
    id: string
    estado_anterior?: EstadoSolicitud
    estado_actual?: EstadoSolicitud
    solucion_final?: string
    fecha_resolucion?: string
  }
}

export interface AdjuntoIntervencionRespuesta {
  mensaje: string
  adjunto: {
    id: string
    solicitud_id: string
    nombre_archivo: string
    tipo_archivo: string
    tamano: number
    fecha_subida: string
  }
}

export async function consultarDetalleSolicitud(
  solicitudId: string,
): Promise<SolicitudDetalle> {
  return api<SolicitudDetalle>(`/requests/${solicitudId}`)
}

export async function actualizarEstadoSolicitud(
  solicitudId: string,
  estado: 'en_atencion' | 'en_espera',
): Promise<RespuestaOperacion> {
  return api<RespuestaOperacion>(`/requests/${solicitudId}/status`, {
    method: 'PATCH',
    datos: { estado },
  })
}

export async function consultarIntervenciones(
  solicitudId: string,
): Promise<IntervencionesRespuesta> {
  return api<IntervencionesRespuesta>(
    `/requests/${solicitudId}/interventions`,
  )
}

export async function registrarIntervencion(
  solicitudId: string,
  datos: {
    descripcion: string
    diagnostico: string
    visibilidad: 'interna' | 'solicitante'
  },
): Promise<Intervencion> {
  return api<Intervencion>(
    `/requests/${solicitudId}/interventions`,
    {
      method: 'POST',
      datos,
    },
  )
}

export async function solicitarInformacion(
  solicitudId: string,
  contenido: string,
): Promise<RespuestaOperacion> {
  return api<RespuestaOperacion>(
    `/requests/${solicitudId}/information-requests`,
    {
      method: 'POST',
      datos: { contenido },
    },
  )
}

export async function registrarSolucion(
  solicitudId: string,
  solucion: string,
): Promise<RespuestaOperacion> {
  return api<RespuestaOperacion>(`/requests/${solicitudId}/resolve`, {
    method: 'POST',
    datos: { solucion },
  })
}

export async function adjuntarImagenIntervencion(
  solicitudId: string,
  intervencionId: string,
  archivo: File,
): Promise<AdjuntoIntervencionRespuesta> {
  const formulario = new FormData()
  formulario.append('archivo', archivo)

  return api<AdjuntoIntervencionRespuesta>(
    `/requests/${solicitudId}/interventions/${intervencionId}/attachments`,
    {
      method: 'POST',
      body: formulario,
    },
  )
}
