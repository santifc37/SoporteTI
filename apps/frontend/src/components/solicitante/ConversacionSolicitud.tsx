
import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'

import { useAuth } from '../../hooks/useAuth'
import { api } from '../../services/api'
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

export function ConversacionSolicitud({
  solicitud,
  onCerrar,
}: ConversacionSolicitudProps) {
  const { usuario } = useAuth()

  const [mensajes, setMensajes] = useState<MensajeConversacion[]>([])
  const [texto, setTexto] = useState('')
  const [cargando, setCargando] = useState(true)
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState('')

  const historialRef = useRef<HTMLDivElement>(null)
  const campoRef = useRef<HTMLTextAreaElement>(null)

  const cerrada = solicitud.estado === 'cerrado'

  async function cargarMensajes() {
    try {
      const respuesta = await api<MensajesPagina>(
        `/requests/${solicitud.id}/messages?page=1&limit=100`,
      )

      setMensajes(
        respuesta.data.map((mensaje) => ({
          ...mensaje,
          estado_envio: 'enviado',
        })),
      )

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
  }

  useEffect(() => {
    void cargarMensajes()
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
  }, [mensajes])

  async function enviarMensaje(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    const contenido = texto.trim()

    if (!contenido || enviando || cerrada || !usuario) return

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
    }

    // Mostrar el mensaje inmediatamente sin esperar al servidor.
    setMensajes((actuales) => [...actuales, mensajeTemporal])
    setTexto('')
    setError('')
    setEnviando(true)

    try {
      await api(`/requests/${solicitud.id}/messages`, {
        method: 'POST',
        datos: { contenido },
      })

      setMensajes((actuales) =>
        actuales.map((mensaje) =>
          mensaje.id === idTemporal
            ? { ...mensaje, estado_envio: 'enviado' }
            : mensaje,
        ),
      )

      // Sin bloquear el chat, sincronizar con el historial del servidor.
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
      await api(`/requests/${solicitud.id}/messages`, {
        method: 'POST',
        datos: { contenido: mensaje.contenido },
      })

      setMensajes((actuales) =>
        actuales.map((actual) =>
          actual.id === mensaje.id
            ? { ...actual, estado_envio: 'enviado' }
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
          ) : mensajes.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center text-center">
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
            className="flex shrink-0 items-end gap-3 border-t border-slate-200 bg-white p-4 sm:px-6 sm:py-5"
          >
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
              disabled={!texto.trim() || enviando}
              className="shrink-0 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {enviando ? 'Enviando...' : 'Enviar'}
            </button>
          </form>
        )}
      </section>
    </div>
  )
}
