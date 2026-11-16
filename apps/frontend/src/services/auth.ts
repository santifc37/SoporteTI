import { api } from './api'
import type {
  LoginRequest,
  LoginResponse,
  MeResponse,
  MensajeResponse,
} from '../types/auth'

export async function iniciarSesion(
  datos: LoginRequest,
): Promise<LoginResponse> {
  return api<LoginResponse>('/auth/login', {
    method: 'POST',
    datos,
  })
}

export async function obtenerUsuario(): Promise<MeResponse> {
  return api<MeResponse>('/auth/me')
}

export async function cerrarSesion(): Promise<MensajeResponse> {
  return api<MensajeResponse>('/auth/logout', {
    method: 'POST',
  })
}