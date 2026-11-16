
export type RolUsuario = 'solicitante' | 'tecnico' | 'coordinador'

export interface Usuario {
  id: string
  nombre: string
  apellido: string
  correo: string
  rol: RolUsuario
  activo?: boolean
}

export interface LoginRequest {
  correo: string
  contrasena: string
}

export interface LoginResponse {
  mensaje: string
  usuario: Omit<Usuario, 'activo'>
}

export interface MeResponse {
  usuario: Usuario
}

export interface MensajeResponse {
  mensaje: string
}
