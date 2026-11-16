
import { api } from './api'
import type { ActualizarPerfilRequest, Usuario } from '../types/auth'

interface ActualizarPerfilResponse {
  mensaje: string
  usuario: Pick<Usuario, 'id' | 'nombre' | 'apellido' | 'correo' | 'rol' | 'activo'>
}

export async function actualizarPerfil(
  usuarioId: string,
  datos: ActualizarPerfilRequest,
): Promise<ActualizarPerfilResponse> {
  return api<ActualizarPerfilResponse>(
    `/users/${encodeURIComponent(usuarioId)}`,
    {
      method: 'PATCH',
      datos,
    },
  )
}
