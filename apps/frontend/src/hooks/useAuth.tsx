
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'

import {
  iniciarSesion,
  obtenerUsuario,
  cerrarSesion,
} from '../services/auth'

import type {
  Usuario,
  LoginRequest,
} from '../types/auth'

interface AuthContextType {
  usuario: Usuario | null
  cargando: boolean
  login: (datos: LoginRequest) => Promise<Usuario>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    async function verificarSesion() {
      try {
        const respuesta = await obtenerUsuario()
        setUsuario(respuesta.usuario)
      } catch {
        setUsuario(null)
      } finally {
        setCargando(false)
      }
    }

    void verificarSesion()
  }, [])

  const login = useCallback(async (datos: LoginRequest): Promise<Usuario> => {
    const respuesta = await iniciarSesion(datos)
    setUsuario(respuesta.usuario)
    return respuesta.usuario
  }, [])

  const logout = useCallback(async () => {
    try {
      await cerrarSesion()
    } finally {
      setUsuario(null)
    }
  }, [])

  return (
    <AuthContext.Provider
      value={{ usuario, cargando, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const contexto = useContext(AuthContext)

  if (!contexto) {
    throw new Error('useAuth debe utilizarse dentro de AuthProvider')
  }

  return contexto
}
