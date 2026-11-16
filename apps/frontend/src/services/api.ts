const API_URL = import.meta.env.VITE_API_URL ?? '/api/v1'

interface OpcionesAPI extends RequestInit {
  datos?: unknown
}

export async function api<T>(
  ruta: string,
  opciones: OpcionesAPI = {},
): Promise<T> {
  const { datos, headers, ...configuracion } = opciones

  const respuesta = await fetch(`${API_URL}${ruta}`, {
    ...configuracion,
    credentials: 'include',
    headers: {
      ...(datos !== undefined
        ? { 'Content-Type': 'application/json' }
        : {}),
      ...headers,
    },
    body: datos !== undefined
      ? JSON.stringify(datos)
      : configuracion.body,
  })

  const contenido = await respuesta.json().catch(() => null)

  if (!respuesta.ok) {
    const mensaje =
      contenido?.error?.mensaje ??
      contenido?.mensaje ??
      'Error al comunicarse con el servidor'

    throw new Error(mensaje)
  }

  return contenido as T
}