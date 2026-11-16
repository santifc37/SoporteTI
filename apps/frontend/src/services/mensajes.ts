
import { api } from './api'

export interface AdjuntoMensaje {
  id: string
  mensaje_id: string
  nombre_archivo: string
  tipo_archivo: string
  tamano: number
  subido_por: string
  fecha_subida: string
  url: string
}

interface AdjuntosMensajeResponse {
  data: AdjuntoMensaje[]
}

interface SubirAdjuntoResponse {
  mensaje: string
  adjunto: {
    id: string
    solicitud_id: string
    mensaje_id: string
    nombre_archivo: string
    tipo_archivo: string
    tamano: number
    fecha_subida: string
  }
}

export async function consultarAdjuntosMensaje(
  solicitudId: string,
  mensajeId: string,
): Promise<AdjuntoMensaje[]> {
  const respuesta = await api<AdjuntosMensajeResponse>(
    `/requests/${encodeURIComponent(solicitudId)}/messages/${encodeURIComponent(mensajeId)}/attachments`,
  )

  return respuesta.data
}

export async function subirAdjuntoMensaje(
  solicitudId: string,
  mensajeId: string,
  archivo: File,
): Promise<SubirAdjuntoResponse> {
  const formulario = new FormData()
  formulario.append('archivo', archivo)

  return api<SubirAdjuntoResponse>(
    `/requests/${encodeURIComponent(solicitudId)}/messages/${encodeURIComponent(mensajeId)}/attachments`,
    {
      method: 'POST',
      body: formulario,
    },
  )
}
