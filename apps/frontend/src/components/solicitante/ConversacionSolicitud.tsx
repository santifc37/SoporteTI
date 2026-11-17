
import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'

import { useAuth } from '../../hooks/useAuth'
import { api } from '../../services/api'
import {
  consultarAdjuntosMensaje,
  subirAdjuntoMensaje,
} from '../../services/mensajes'
import type { AdjuntoMensaje } from '../../services/mensajes'
import type { SolicitudResumen } from '../../types/solicitud'

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

interface PeticionInformacion {
  id: string
  contenido: string
  estado: string
  solicitado_por: {
    id: string
    nombre: string
    rol: string
  }
  fecha_solicitud: string
  respuesta: {
    id: string
    solicitud_informacion_id: string
    respondido_por: string
    contenido: string
    fecha_respuesta: string
  } | null
}

interface PeticionesInformacionRespuesta {
  data: PeticionInformacion[]
}

interface ConversacionSolicitudProps {
  solicitud: SolicitudResumen
  onCerrar: () => void
}

function formatearHora(fecha: string): string {
  const valor = new Date(fecha)

  if (Number.isNaN(valor.getTime())) return ''

  return new Intl.DateTimeFormat('es-CO', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(valor)
}

function formatearFecha(fecha: string): string {
  const valor = new Date(fecha)

  if (Number.isNaN(valor.getTime())) return ''

  return new Intl.DateTimeFormat('es-CO', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(valor)
}

export function ConversacionSolicitud({
  solicitud,
  onCerrar,
}: ConversacionSolicitudProps) {
  const { usuario } = useAuth()

  const [mensajes, setMensajes] = useState<MensajeConversacion[]>([])
  const [peticionesInformacion, setPeticionesInformacion] = useState<
    PeticionInformacion[]
  >([])

  const [texto, setTexto] = useState('')
  const [archivo, setArchivo] = useState<File | null>(null)
  const [cargando, setCargando] = useState(true)
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState('')

  const [respuestas, setRespuestas] = useState<Record<string, string>>({})
  const [peticionRespondiendo, setPeticionRespondiendo] = useState<
    string | null
  >(null)

  const historialRef = useRef<HTMLDivElement>(null)
  const campoRef = useRef<HTMLTextAreaElement>(null)
  const archivoRef = useRef<HTMLInputElement>(null)

  const cerrada = solicitud.estado === 'cerrado'
  const [vistaPrevia, setVistaPrevia] = useState<string | null>(null)

  async function cargarMensajes() {
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
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible cargar la conversación.',
      )
    } finally {
      setCargando(false)
    }
  }

  async function cargarPeticionesInformacion() {
    try {
      const respuesta = await api<PeticionesInformacionRespuesta>(
        `/requests/${solicitud.id}/information-requests`,
      )

      setPeticionesInformacion(respuesta.data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible consultar las solicitudes de información.',
      )
    }
  }

  useEffect(() => {
    void cargarMensajes()
    void cargarPeticionesInformacion()

    // Actualiza las peticiones periódicamente mientras el chat está abierto.
    const intervalo = window.setInterval(() => {
      void cargarPeticionesInformacion()
    }, 15000)

    return () => {
      window.clearInterval(intervalo)
    }

    // La conversación corresponde a una solicitud concreta.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [solicitud.id])

  useEffect(() => {
    const historial = historialRef.current

    if (!historial) return

    historial.scrollTo({
      top: historial.scrollHeight,
      behavior: 'smooth',
    })
  }, [mensajes, peticionesInformacion])

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

  async function enviarRespuestaInformacion(
    evento: FormEvent<HTMLFormElement>,
    peticion: PeticionInformacion,
  ) {
    evento.preventDefault()

    const contenido = (respuestas[peticion.id] ?? '').trim()

    if (!contenido || peticionRespondiendo) return

    setPeticionRespondiendo(peticion.id)
    setError('')

    try {
      await api<unknown>(
        `/information-requests/${peticion.id}/responses`,
        {
          method: 'POST',
          datos: { contenido },
        },
      )

      setRespuestas((actuales) => ({
        ...actuales,
        [peticion.id]: '',
      }))

      await cargarPeticionesInformacion()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible enviar la respuesta.',
      )
    } finally {
      setPeticionRespondiendo(null)
    }
  }

  async function enviarMensaje(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    const contenido = texto.trim()

    if ((!contenido && !archivo) || enviando || cerrada || !usuario) {
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
          : 'No fue posible enviar el mensaje. Puedes reintentarlo.',
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
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/60 p-2 sm:p-5">
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-conversacion"
        className="flex h-[94dvh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 shadow-2xl"
      >
        <header className="flex shrink-0 items-center justify-between gap-4 border-b border-slate-200 bg-white px-5 py-4 sm:px-7">
          <div className="min-w-0">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              {solicitud.numero}
            </p>

            <h2
              id="titulo-conversacion"
              className="mt-1 truncate text-lg font-bold text-slate-900 sm:text-xl"
            >
              Conversación
            </h2>

            <p className="mt-1 truncate text-sm text-slate-500">
              {solicitud.titulo}
            </p>
          </div>

          <button
            type="button"
            onClick={onCerrar}
            aria-label="Cerrar conversación"
            className="shrink-0 rounded-lg border border-slate-300 px-3 py-1.5 text-xl text-slate-600 transition hover:bg-slate-100"
          >
            ×
          </button>
        </header>

        <div
          ref={historialRef}
          className="min-h-0 flex-1 space-y-4 overflow-y-auto bg-slate-100/80 p-4 sm:p-7"
        >
          {cargando ? (
            <p className="py-10 text-center text-sm text-slate-500">
              Cargando conversación...
            </p>
          ) : (
            <>
              {mensajes.length === 0 && peticionesInformacion.length === 0 ? (
                <div className="flex min-h-48 flex-col items-center justify-center text-center">
                  <div className="flex h-14 w-14 items-center justify-center rounded-full bg-white text-2xl text-slate-400 shadow-sm">
                    ☰
                  </div>

                  <p className="mt-4 font-semibold text-slate-700">
                    Todavía no hay mensajes
                  </p>

                  <p className="mt-1 text-sm text-slate-500">
                    Escribe el primer mensaje para iniciar la conversación.
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
                        className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm sm:max-w-[70%] ${
                          propio
                            ? 'rounded-br-sm bg-blue-600 text-white'
                            : 'rounded-bl-sm border border-slate-200 bg-white text-slate-800'
                        }`}
                      >
                        {!propio && (
                          <p className="mb-1 text-xs font-bold text-blue-700">
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
                                    title="Abrir imagen en otra pestaña"
                                    className="block overflow-hidden rounded-xl"
                                  >
                                    <img
                                      src={adjunto.url}
                                      alt={adjunto.nombre_archivo}
                                      loading="lazy"
                                      className="max-h-80 w-full rounded-xl object-contain transition hover:opacity-90"
                                    />
                                  </a>
                                ) : (
                                  <p className="text-xs">
                                    No se pudo cargar la imagen:{' '}
                                    {adjunto.nombre_archivo}
                                  </p>
                                )}

                                <p
                                  className={`mt-1 break-all text-xs ${
                                    propio ? 'text-blue-100' : 'text-slate-500'
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
                            propio ? 'text-blue-100' : 'text-slate-400'
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

              {peticionesInformacion.map((peticion) => {
                const respondida =
                  peticion.estado.toLowerCase() === 'respondida' ||
                  peticion.respuesta !== null

                return (
                  <div
                    key={peticion.id}
                    className="flex justify-start"
                  >
                    <article className="w-full max-w-[90%] rounded-2xl border border-amber-300 bg-amber-50 p-4 shadow-sm sm:max-w-[80%]">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-amber-100 text-amber-800">
                            ?
                          </span>

                          <div>
                            <p className="text-sm font-bold text-amber-950">
                              Solicitud de información
                            </p>
                            <p className="text-xs text-amber-800">
                              {peticion.solicitado_por.nombre}
                            </p>
                          </div>
                        </div>

                        <span
                          className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                            respondida
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-amber-200 text-amber-900'
                          }`}
                        >
                          {respondida ? 'Respondida' : 'Pendiente'}
                        </span>
                      </div>

                      <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-amber-950">
                        {peticion.contenido}
                      </p>

                      <p className="mt-2 text-xs text-amber-800">
                        Solicitada el {formatearFecha(peticion.fecha_solicitud)}
                      </p>

                      {peticion.respuesta ? (
                        <div className="mt-4 rounded-xl border border-emerald-200 bg-white p-3">
                          <p className="text-xs font-bold uppercase tracking-wide text-emerald-800">
                            Tu respuesta
                          </p>

                          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-slate-800">
                            {peticion.respuesta.contenido}
                          </p>

                          <p className="mt-2 text-xs text-slate-500">
                            {formatearFecha(
                              peticion.respuesta.fecha_respuesta,
                            )}
                          </p>
                        </div>
                      ) : !respondida && !cerrada ? (
                        <form
                          onSubmit={(evento) =>
                            void enviarRespuestaInformacion(evento, peticion)
                          }
                          className="mt-4 space-y-3 border-t border-amber-200 pt-4"
                        >
                          <label
                            htmlFor={`respuesta-${peticion.id}`}
                            className="block text-sm font-semibold text-amber-950"
                          >
                            Escribe tu respuesta
                          </label>

                          <textarea
                            id={`respuesta-${peticion.id}`}
                            rows={3}
                            maxLength={5000}
                            required
                            value={respuestas[peticion.id] ?? ''}
                            onChange={(evento) =>
                              setRespuestas((actuales) => ({
                                ...actuales,
                                [peticion.id]: evento.target.value,
                              }))
                            }
                            placeholder="Escribe aquí la información solicitada..."
                            disabled={peticionRespondiendo === peticion.id}
                            className="w-full resize-y rounded-lg border border-amber-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-100"
                          />

                          <div className="flex justify-end">
                            <button
                              type="submit"
                              disabled={
                                !respuestas[peticion.id]?.trim() ||
                                peticionRespondiendo !== null
                              }
                              className="rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                              {peticionRespondiendo === peticion.id
                                ? 'Enviando respuesta...'
                                : 'Enviar respuesta'}
                            </button>
                          </div>
                        </form>
                      ) : (
                        <p className="mt-4 rounded-lg bg-white/70 p-3 text-sm text-slate-600">
                          Esta solicitud ya no admite respuestas.
                        </p>
                      )}
                    </article>
                  </div>
                )
              })}
            </>
          )}
        </div>

        {error && (
          <div className="shrink-0 border-t border-red-200 bg-red-50 px-5 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        {cerrada ? (
          <div className="shrink-0 border-t border-slate-200 bg-white px-5 py-4 text-center text-sm text-slate-500">
            Esta solicitud está cerrada. Puedes consultar los mensajes, pero
            no enviar nuevos.
          </div>
        ) : (
          <form
            onSubmit={enviarMensaje}
            className="shrink-0 border-t border-slate-200 bg-white p-4 sm:px-6 sm:py-5"
          >
            {archivo && vistaPrevia && (
              <div className="mb-3 flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
                <img
                  src={vistaPrevia}
                  alt="Vista previa del adjunto"
                  className="h-16 w-16 rounded-lg object-cover"
                />

                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold text-slate-700">
                    {archivo.name}
                  </p>
                  <p className="text-xs text-slate-500">
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

            <div className="flex items-end gap-3">
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
                className="shrink-0 rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-xl text-slate-600 transition hover:bg-slate-100 disabled:opacity-50"
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
                placeholder="Escribe tu mensaje..."
                className="max-h-32 min-h-12 flex-1 resize-y rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />

              <button
                type="submit"
                disabled={(!texto.trim() && !archivo) || enviando}
                className="shrink-0 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {enviando ? 'Enviando...' : 'Enviar'}
              </button>
            </div>

            <p className="mt-2 pl-1 text-xs text-slate-400">
              Puedes adjuntar imágenes de hasta 10 MB.
            </p>
          </form>
        )}
      </section>
    </div>
  )
}
