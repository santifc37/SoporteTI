import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import type { RolUsuario } from '../types/auth'

interface RutaProtegidaProps {
  rolesPermitidos?: RolUsuario[]
}

export function RutaProtegida({
  rolesPermitidos,
}: RutaProtegidaProps) {
  const { usuario, cargando } = useAuth()

  if (cargando) {
    return <p className="p-6 text-center">Verificando sesión...</p>
  }

  if (!usuario) {
    return <Navigate to="/login" replace />
  }

  if (
    rolesPermitidos &&
    !rolesPermitidos.includes(usuario.rol)
  ) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}