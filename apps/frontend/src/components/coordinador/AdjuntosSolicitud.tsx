
import { useEffect, useState } from 'react'

import { descargarAdjunto } from '../../services/coordinador'
import type { AdjuntoSolicitud } from '../../types/coordinador'
import { CLASE_TARJETA, formatearFecha, mensajeDeError } from './etiquetas'

function formatearTamano(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

/** Miniatura que descarga la imagen con la sesión del usuario (RF-08). */
function Miniatura({ adjunto }: { adjunto: AdjuntoSolicitud }) {
  const [url, setUrl] = useState<string | null>(null)
  const [fallo, setFallo] = useState(false)

  const esImagen = adjunto.tipo_archivo.startsWith('image/')

  useEffect(() => {
    if (!esImagen) return

    let vigente = true
    let creada: string | null = null

    descargarAdjunto(adjunto.id)
      .then((blob) => {
        if (!vigente) return
        creada = URL.createObjectURL(blob)
        setUrl(creada)
      })
      .catch(() => {
        if (vigente) setFallo(true)
      })

    return () => {
      vigente = false
      if (creada) URL.revokeObjectURL(creada)
    }
  }, [adjunto.id, esImagen])

  if (!esImagen || fallo) {
    return (
      <div className="flex h-28 items-center justify-center rounded-lg bg-panel text-xs font-semibold uppercase text-texto-secundario">
        {adjunto.tipo_archivo.split('/')[1] ?? 'archivo'}
      </div>
    )
  }

  if (!url) {
    return <div className="h-28 animate-pulse rounded-lg bg-panel" />
  }

  return (
    <img
      src={url}
      alt={adjunto.nombre_archivo}
      className="h-28 w-full rounded-lg object-cover"
    />
  )
}

export function AdjuntosSolicitud({
  adjuntos,
}: {
  adjuntos: AdjuntoSolicitud[]
}) {
  const [error, setError] = useState('')

  async function abrir(adjunto: AdjuntoSolicitud) {
    setError('')

    try {
      const blob = await descargarAdjunto(adjunto.id)
      const url = URL.createObjectURL(blob)
      window.open(url, '_blank', 'noopener')
      // Se libera después de que la pestaña nueva haya cargado el archivo.
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000)
    } catch (err) {
      setError(mensajeDeError(err, 'No fue posible abrir el archivo.'))
    }
  }

  return (
    <div className={CLASE_TARJETA}>
      <h2 className="text-lg font-semibold text-texto">
        Archivos adjuntos
      </h2>
      <p className="mt-1 text-sm text-texto-secundario">
        Evidencias que el solicitante agregó al registrar el caso.
      </p>

      {error && (
        <p className="mt-3 text-sm font-medium text-error">{error}</p>
      )}

      {adjuntos.length > 0 ? (
        <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {adjuntos.map((adjunto) => (
            <button
              key={adjunto.id}
              type="button"
              onClick={() => void abrir(adjunto)}
              className="rounded-lg border border-panel bg-fondo p-3 text-left transition hover:border-blue-300 hover:shadow-md"
            >
              <Miniatura adjunto={adjunto} />
              <p className="mt-2 truncate text-sm font-medium text-texto">
                {adjunto.nombre_archivo}
              </p>
              <p className="mt-0.5 text-xs text-texto-secundario">
                {formatearTamano(adjunto.tamano)} ·{' '}
                {formatearFecha(adjunto.fecha_subida)}
              </p>
            </button>
          ))}
        </div>
      ) : (
        <p className="mt-5 rounded-lg bg-fondo p-5 text-center text-sm text-texto-secundario">
          Esta solicitud no tiene archivos adjuntos.
        </p>
      )}
    </div>
  )
}
