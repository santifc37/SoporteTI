
export type RolUsuario = 'solicitante' | 'tecnico' | 'coordinador'

export type MedioContacto = 'correo' | 'telefono'

export interface Usuario {
  id: string
  nombre: string
  apellido: string
  correo: string
  rol: RolUsuario
  activo?: boolean
  telefono?: string | null
  medio_contacto_preferido?: MedioContacto
}

export interface LoginRequest {
  correo: string
  contrasena: string
}

export interface LoginResponse {
  mensaje: string
  usuario: Omit<Usuario, 'activo' | 'telefono' | 'medio_contacto_preferido'>
}

export interface MeResponse {
  usuario: Usuario
}

export interface ActualizarPerfilRequest {
  nombre?: string
  apellido?: string
  telefono?: string | null
  medio_contacto_preferido?: MedioContacto
}

export interface MensajeResponse {
  mensaje: string
}
