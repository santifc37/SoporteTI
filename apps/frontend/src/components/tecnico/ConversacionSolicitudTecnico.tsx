
import { useCallback, useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'

import { useAuth } from '../../hooks/useAuth'
import { api } from '../../services/api'
import {
  consultarAdjuntosMensaje,
  subirAdjuntoMensaje,
} from '../../services/mensajes'
import type { AdjuntoMensaje } from '../../services/mensajes'
import type { SolicitudDetalle } from '../../services/tecnico'

interface MensajeConversacion {
  id: string
  solicitud_id: string
  remitente: {
    id: string
    nombre: string
    rol: string
  }
  contenido: string
  fecha_envio: string
  estado_envio?: 'enviando' | 'enviado' | 'error'
  adjuntos?: AdjuntoMensaje[]
}

interface MensajesPagina {
  data: MensajeConversacion[]
  pagination: {
    page: number
    limit: number
    total: number
    total_pages: number
  }
}

interface MensajeEnviadoRespuesta {
  mensaje: string
  data: {
    id: string
    solicitud_id: string
    remitente_id: string
    contenido: string
    fecha_envio: string
  }
}

function formatearHora(fecha: string): string {
  const valor = new Date(fecha)

  if (Number.isNaN(valor.getTime())) return ''

  return new Intl.DateTimeFormat('es-CO', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(valor)
}

export function ConversacionSolicitudTecnico({
  solicitud,
}: {
  solicitud: SolicitudDetalle
}) {
  const { usuario } = useAuth()

  const [mensajes, setMensajes] = useState<MensajeConversacion[]>([])
  const [texto, setTexto] = useState('')
  const [archivo, setArchivo] = useState<File | null>(null)
  const [cargando, setCargando] = useState(true)
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState('')
  const [vistaPrevia, setVistaPrevia] = useState<string | null>(null)

  const historialRef = useRef<HTMLDivElement>(null)
  const campoRef = useRef<HTMLTextAreaElement>(null)
  const archivoRef = useRef<HTMLInputElement>(null)

  const finalizada =
    solicitud.estado === 'resuelto' || solicitud.estado === 'cerrado'

  const cargarMensajes = useCallback(async () => {
    try {
      const respuesta = await api<MensajesPagina>(
        `/requests/${solicitud.id}/messages?page=1&limit=100`,
      )

      const mensajesConAdjuntos = await Promise.all(
        respuesta.data.map(async (mensaje) => {
          try {
            const adjuntos = await consultarAdjuntosMensaje(
              solicitud.id,
              mensaje.id,
            )

            return {
              ...mensaje,
              estado_envio: 'enviado' as const,
              adjuntos,
            }
          } catch {
            return {
              ...mensaje,
              estado_envio: 'enviado' as const,
              adjuntos: [],
            }
          }
        }),
      )

      setMensajes(mensajesConAdjuntos)
      setError('')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible cargar la conversación.',
      )
    } finally {
      setCargando(false)
    }
  }, [solicitud.id])

  useEffect(() => {
    void cargarMensajes()
  }, [cargarMensajes])

  useEffect(() => {
    const historial = historialRef.current

    if (!historial) return

    historial.scrollTo({
      top: historial.scrollHeight,
      behavior: 'smooth',
    })
  }, [mensajes])

  useEffect(() => {
    if (!archivo) {
      setVistaPrevia(null)
      return
    }

    const url = URL.createObjectURL(archivo)
    setVistaPrevia(url)

    return () => URL.revokeObjectURL(url)
  }, [archivo])

  function seleccionarArchivo(nuevoArchivo: File | undefined) {
    if (!nuevoArchivo) return

    if (!nuevoArchivo.type.startsWith('image/')) {
      setError('Solo puedes adjuntar imágenes.')
      return
    }

    if (nuevoArchivo.size > 10 * 1024 * 1024) {
      setError('La imagen no puede superar los 10 MB.')
      return
    }

    setArchivo(nuevoArchivo)
    setError('')
  }

  function quitarArchivo() {
    setArchivo(null)

    if (archivoRef.current) {
      archivoRef.current.value = ''
    }
  }

  async function enviarMensaje(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    const contenido = texto.trim()

    if ((!contenido && !archivo) || enviando || finalizada || !usuario) {
      return
    }

    if (!contenido) {
      setError('Escribe un mensaje para acompañar la imagen.')
      return
    }

    const archivoSeleccionado = archivo
    const idTemporal = `temporal-${Date.now()}`

    const mensajeTemporal: MensajeConversacion = {
      id: idTemporal,
      solicitud_id: solicitud.id,
      remitente: {
        id: usuario.id,
        nombre: `${usuario.nombre} ${usuario.apellido}`.trim(),
        rol: usuario.rol,
      },
      contenido,
      fecha_envio: new Date().toISOString(),
      estado_envio: 'enviando',
      adjuntos: [],
    }

    setMensajes((actuales) => [...actuales, mensajeTemporal])
    setTexto('')
    setArchivo(null)

    if (archivoRef.current) {
      archivoRef.current.value = ''
    }

    setError('')
    setEnviando(true)

    try {
      const respuesta = await api<MensajeEnviadoRespuesta>(
        `/requests/${solicitud.id}/messages`,
        {
          method: 'POST',
          datos: { contenido },
        },
      )

      const mensajeId = respuesta.data.id

      setMensajes((actuales) =>
        actuales.map((mensaje) =>
          mensaje.id === idTemporal
            ? {
                ...mensaje,
                id: mensajeId,
                estado_envio: 'enviado',
              }
            : mensaje,
        ),
      )

      if (archivoSeleccionado) {
        try {
          await subirAdjuntoMensaje(
            solicitud.id,
            mensajeId,
            archivoSeleccionado,
          )

          const adjuntos = await consultarAdjuntosMensaje(
            solicitud.id,
            mensajeId,
          )

          setMensajes((actuales) =>
            actuales.map((mensaje) =>
              mensaje.id === mensajeId
                ? { ...mensaje, adjuntos }
                : mensaje,
            ),
          )
        } catch (err) {
          setError(
            err instanceof Error
              ? `El mensaje se envió, pero no se pudo adjuntar la imagen: ${err.message}`
              : 'El mensaje se envió, pero no se pudo adjuntar la imagen.',
          )
        }
      }

      void cargarMensajes()
    } catch (err) {
      setMensajes((actuales) =>
        actuales.map((mensaje) =>
          mensaje.id === idTemporal
            ? { ...mensaje, estado_envio: 'error' }
            : mensaje,
        ),
      )

      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible enviar el mensaje.',
      )
    } finally {
      setEnviando(false)
      campoRef.current?.focus()
    }
  }

  async function reintentarMensaje(mensaje: MensajeConversacion) {
    if (enviando) return

    setError('')
    setEnviando(true)

    setMensajes((actuales) =>
      actuales.map((actual) =>
        actual.id === mensaje.id
          ? { ...actual, estado_envio: 'enviando' }
          : actual,
      ),
    )

    try {
      const respuesta = await api<MensajeEnviadoRespuesta>(
        `/requests/${solicitud.id}/messages`,
        {
          method: 'POST',
          datos: { contenido: mensaje.contenido },
        },
      )

      setMensajes((actuales) =>
        actuales.map((actual) =>
          actual.id === mensaje.id
            ? {
                ...actual,
                id: respuesta.data.id,
                estado_envio: 'enviado',
              }
            : actual,
        ),
      )

      void cargarMensajes()
    } catch (err) {
      setMensajes((actuales) =>
        actuales.map((actual) =>
          actual.id === mensaje.id
            ? { ...actual, estado_envio: 'error' }
            : actual,
        ),
      )

      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible reenviar el mensaje.',
      )
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section className="overflow-hidden rounded-xl border border-panel bg-tarjeta shadow-sm">
      <header className="flex items-center justify-between gap-3 border-b border-panel px-5 py-4">
        <div>
          <h2 className="text-lg font-semibold text-texto">
            Conversación con el solicitante
          </h2>
          <p className="mt-1 text-sm text-texto-secundario">
            Mensajes relacionados con esta solicitud.
          </p>
        </div>

        <span className="shrink-0 rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-800">
          {mensajes.length} mensajes
        </span>
      </header>

      {/* Solo esta zona tiene scroll y altura limitada */}
      <div
        ref={historialRef}
        className="h-[450px] max-h-[550px] space-y-4 overflow-y-auto overscroll-contain bg-fondo p-4 sm:p-5"
      >
        {cargando ? (
          <p className="py-10 text-center text-sm text-texto-secundario">
            Cargando conversación...
          </p>
        ) : mensajes.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-tarjeta text-2xl text-texto-secundario">
              ☰
            </div>

            <p className="mt-3 font-semibold text-texto">
              Todavía no hay mensajes
            </p>

            <p className="mt-1 text-sm text-texto-secundario">
              Inicia la conversación con el solicitante.
            </p>
          </div>
        ) : (
          mensajes.map((mensaje) => {
            const propio = mensaje.remitente.id === usuario?.id

            return (
              <div
                key={mensaje.id}
                className={`flex ${propio ? 'justify-end' : 'justify-start'}`}
              >
                <article
                  className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm sm:max-w-[75%] ${
                    propio
                      ? 'rounded-br-sm bg-blue-600 text-white'
                      : 'rounded-bl-sm border border-panel bg-tarjeta text-texto'
                  }`}
                >
                  {!propio && (
                    <p className="mb-1 text-xs font-bold text-accion">
                      {mensaje.remitente.nombre}
                    </p>
                  )}

                  <p className="whitespace-pre-wrap break-words text-sm leading-relaxed">
                    {mensaje.contenido}
                  </p>

                  {mensaje.adjuntos && mensaje.adjuntos.length > 0 && (
                    <div className="mt-3 space-y-3">
                      {mensaje.adjuntos.map((adjunto) => (
                        <div key={adjunto.id}>
                          {adjunto.url ? (
                            <a
                              href={adjunto.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              title="Abrir imagen"
                              className="block overflow-hidden rounded-xl"
                            >
                              <img
                                src={adjunto.url}
                                alt={adjunto.nombre_archivo}
                                loading="lazy"
                                className="max-h-64 w-full rounded-xl object-contain"
                              />
                            </a>
                          ) : (
                            <p className="text-xs">
                              No se pudo cargar la imagen: {adjunto.nombre_archivo}
                            </p>
                          )}

                          <p
                            className={`mt-1 break-all text-xs ${
                              propio ? 'text-blue-100' : 'text-texto-secundario'
                            }`}
                          >
                            {adjunto.nombre_archivo}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}

                  <div
                    className={`mt-2 flex items-center justify-end gap-2 text-[11px] ${
                      propio ? 'text-blue-100' : 'text-texto-secundario'
                    }`}
                  >
                    <span>{formatearHora(mensaje.fecha_envio)}</span>

                    {propio && mensaje.estado_envio === 'enviando' && (
                      <span>Enviando...</span>
                    )}

                    {propio && mensaje.estado_envio === 'enviado' && (
                      <span>Enviado ✓</span>
                    )}

                    {propio && mensaje.estado_envio === 'error' && (
                      <button
                        type="button"
                        onClick={() => void reintentarMensaje(mensaje)}
                        className="font-bold underline"
                      >
                        Reintentar
                      </button>
                    )}
                  </div>
                </article>
              </div>
            )
          })
        )}
      </div>

      {error && (
        <div className="border-t border-red-200 bg-red-50 px-5 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {finalizada ? (
        <div className="border-t border-panel bg-tarjeta px-5 py-4 text-center text-sm text-texto-secundario">
          Esta solicitud está finalizada. Puedes consultar los mensajes, pero
          no enviar nuevos.
        </div>
      ) : (
        <form
          onSubmit={enviarMensaje}
          className="border-t border-panel bg-tarjeta p-4 sm:p-5"
        >
          {archivo && vistaPrevia && (
            <div className="mb-3 flex items-center gap-3 rounded-xl border border-panel bg-fondo p-3">
              <img
                src={vistaPrevia}
                alt="Vista previa del adjunto"
                className="h-14 w-14 rounded-lg object-cover"
              />

              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-texto">
                  {archivo.name}
                </p>
                <p className="text-xs text-texto-secundario">
                  {(archivo.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>

              <button
                type="button"
                onClick={quitarArchivo}
                disabled={enviando}
                className="rounded-lg px-3 py-2 text-sm font-semibold text-red-600 hover:bg-red-50 disabled:opacity-50"
              >
                Quitar
              </button>
            </div>
          )}

          <div className="flex items-end gap-2 sm:gap-3">
            <input
              ref={archivoRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(evento) =>
                seleccionarArchivo(evento.target.files?.[0])
              }
            />

            <button
              type="button"
              onClick={() => archivoRef.current?.click()}
              disabled={enviando}
              title="Adjuntar imagen"
              aria-label="Adjuntar imagen"
              className="shrink-0 rounded-xl border border-panel bg-fondo px-4 py-3 text-xl text-texto-secundario transition hover:bg-panel disabled:opacity-50"
            >
              +
            </button>

            <textarea
              ref={campoRef}
              value={texto}
              onChange={(evento) => setTexto(evento.target.value)}
              onKeyDown={(evento) => {
                if (
                  evento.key === 'Enter' &&
                  !evento.shiftKey &&
                  !evento.nativeEvent.isComposing
                ) {
                  evento.preventDefault()
                  evento.currentTarget.form?.requestSubmit()
                }
              }}
              rows={2}
              maxLength={5000}
              placeholder="Escribe un mensaje..."
              className="max-h-32 min-h-12 min-w-0 flex-1 resize-y rounded-xl border border-panel bg-fondo px-4 py-3 text-sm text-texto outline-none transition placeholder:text-texto-secundario focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
            />

            <button
              type="submit"
              disabled={(!texto.trim() && !archivo) || enviando}
              className="shrink-0 rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {enviando ? 'Enviando...' : 'Enviar'}
            </button>
          </div>

          <p className="mt-2 pl-1 text-xs text-texto-secundario">
            Puedes adjuntar imágenes de hasta 10 MB.
          </p>
        </form>
      )}
    </section>
  )
}
