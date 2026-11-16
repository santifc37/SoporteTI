
import { useEffect, useMemo, useRef, useState } from 'react'
import type { FormEvent } from 'react'

import { Boton } from '../../components/Boton'
import { Cargando } from '../../components/Cargando'
import { MensajeEstado } from '../../components/MensajeEstado'
import { useAuth } from '../../hooks/useAuth'
import { api } from '../../services/api'

import type {
  EstadoSolicitud,
  PrioridadSolicitud,
  SolicitudResumen,
  SolicitudesPagina,
  TipoSolicitud,
} from '../../types/solicitud'

interface Categoria {
  id: string
  nombre: string
}

interface CategoriasPagina {
  data: Categoria[]
}

interface FormularioSolicitud {
  titulo: string
  descripcion: string
  tipo: TipoSolicitud
  categoria_id: string
  ubicacion: string
  placa_equipo: string
  medio_contacto: 'correo' | 'telefono'
  dato_contacto: string
}

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

const FORMULARIO_INICIAL: FormularioSolicitud = {
  titulo: '',
  descripcion: '',
  tipo: 'incidente',
  categoria_id: '',
  ubicacion: '',
  placa_equipo: '',
  medio_contacto: 'correo',
  dato_contacto: '',
}

const NOMBRES_ESTADO: Record<EstadoSolicitud, string> = {
  registrado: 'Registrado',
  en_evaluacion: 'En evaluación',
  asignado: 'Asignado',
  en_atencion: 'En atención',
  en_espera: 'En espera',
  resuelto: 'Resuelto',
  cerrado: 'Cerrado',
}

const ESTILOS_ESTADO: Record<EstadoSolicitud, string> = {
  registrado: 'bg-slate-100 text-slate-700',
  en_evaluacion: 'bg-blue-100 text-blue-800',
  asignado: 'bg-indigo-100 text-indigo-800',
  en_atencion: 'bg-amber-100 text-amber-800',
  en_espera: 'bg-orange-100 text-orange-800',
  resuelto: 'bg-emerald-100 text-emerald-800',
  cerrado: 'bg-slate-200 text-slate-700',
}

const PRIORIDAD_ORDEN: Record<PrioridadSolicitud, number> = {
  alta: 0,
  media: 1,
  baja: 2,
}

const CAMPO =
  'mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 hover:border-slate-400 focus:border-blue-600 focus:ring-2 focus:ring-blue-100'

const ETIQUETA = 'block text-sm font-semibold text-slate-700'

function formatearFecha(fecha: string): string {
  const valor = new Date(fecha)

  if (Number.isNaN(valor.getTime())) {
    return 'Fecha no disponible'
  }

  return new Intl.DateTimeFormat('es-CO', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(valor)
}

function formatearHora(fecha: string): string {
  const valor = new Date(fecha)

  if (Number.isNaN(valor.getTime())) return ''

  return new Intl.DateTimeFormat('es-CO', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(valor)
}

function ordenarSolicitudes(solicitudes: SolicitudResumen[]) {
  return [...solicitudes].sort((a, b) => {
    const aCerrada = a.estado === 'cerrado' || a.estado === 'resuelto'
    const bCerrada = b.estado === 'cerrado' || b.estado === 'resuelto'

    if (aCerrada !== bCerrada) {
      return Number(aCerrada) - Number(bCerrada)
    }

    const prioridadA = a.prioridad ? PRIORIDAD_ORDEN[a.prioridad] : 3
    const prioridadB = b.prioridad ? PRIORIDAD_ORDEN[b.prioridad] : 3

    if (prioridadA !== prioridadB) {
      return prioridadA - prioridadB
    }

    return (
      new Date(b.fecha_creacion).getTime() -
      new Date(a.fecha_creacion).getTime()
    )
  })
}

function TarjetaSolicitud({
  solicitud,
  onVerConversacion,
}: {
  solicitud: SolicitudResumen
  onVerConversacion: () => void
}) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-300 hover:shadow-md">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            {solicitud.numero}
          </p>
          <h3 className="mt-1 break-words text-base font-semibold text-slate-900">
            {solicitud.titulo}
          </h3>
        </div>

        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold ${ESTILOS_ESTADO[solicitud.estado]}`}
        >
          {NOMBRES_ESTADO[solicitud.estado]}
        </span>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-slate-100 pt-3 text-sm">
        <p className="text-slate-600">
          <span className="font-medium text-slate-800">Tipo:</span>{' '}
          <span className="capitalize">{solicitud.tipo}</span>
        </p>

        <p className="text-slate-600">
          <span className="font-medium text-slate-800">Prioridad:</span>{' '}
          <span className="capitalize">
            {solicitud.prioridad ?? 'Pendiente'}
          </span>
        </p>

        <p className="text-slate-600">
          <span className="font-medium text-slate-800">Categoría:</span>{' '}
          {solicitud.categoria?.nombre ?? 'Sin categoría'}
        </p>

        <p className="text-slate-500">
          {formatearFecha(solicitud.fecha_creacion)}
        </p>
      </div>

      <div className="mt-4 border-t border-slate-100 pt-3">
        <button
          type="button"
          onClick={onVerConversacion}
          className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 transition hover:bg-blue-100"
        >
          Ver conversación
        </button>
      </div>
    </article>
  )
}

function ConversacionSolicitud({
  solicitud,
  onCerrar,
}: {
  solicitud: SolicitudResumen
  onCerrar: () => void
}) {
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

    // Mostrar inmediatamente el mensaje, sin esperar al servidor.
    setMensajes((actuales) => [...actuales, mensajeTemporal])
    setTexto('')
    setError('')
    setEnviando(true)

    try {
      await api(`/requests/${solicitud.id}/messages`, {
        method: 'POST',
        datos: { contenido },
      })

      // El servidor confirmó el guardado.
      setMensajes((actuales) =>
        actuales.map((mensaje) =>
          mensaje.id === idTemporal
            ? { ...mensaje, estado_envio: 'enviado' }
            : mensaje,
        ),
      )

      // Sin bloquear la conversación, sincronizar con el historial real.
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

function FormularioNuevaSolicitud({
  onCerrar,
  onCreada,
}: {
  onCerrar: () => void
  onCreada: () => void
}) {
  const [formulario, setFormulario] =
    useState<FormularioSolicitud>(FORMULARIO_INICIAL)
  const [categorias, setCategorias] = useState<Categoria[]>([])
  const [cargandoCategorias, setCargandoCategorias] = useState(true)
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let vigente = true

    api<CategoriasPagina>('/categories?limit=100')
      .then((respuesta) => {
        if (vigente) setCategorias(respuesta.data)
      })
      .catch(() => {
        if (vigente) setError('No fue posible cargar las categorías.')
      })
      .finally(() => {
        if (vigente) setCargandoCategorias(false)
      })

    return () => {
      vigente = false
    }
  }, [])

  function actualizar<K extends keyof FormularioSolicitud>(
    campo: K,
    valor: FormularioSolicitud[K],
  ) {
    setFormulario((actual) => ({
      ...actual,
      [campo]: valor,
    }))
  }

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError('')
    setEnviando(true)

    try {
      await api('/requests', {
        method: 'POST',
        datos: {
          titulo: formulario.titulo.trim(),
          descripcion: formulario.descripcion.trim(),
          tipo: formulario.tipo,
          categoria_id: formulario.categoria_id || null,
          ubicacion: formulario.ubicacion.trim(),
          placa_equipo: formulario.placa_equipo.trim() || null,
          medio_contacto: formulario.medio_contacto,
          dato_contacto: formulario.dato_contacto.trim(),
        },
      })

      onCreada()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible registrar la solicitud.',
      )
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-950/60 p-2 sm:p-4">
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-nueva-solicitud"
        className="flex max-h-[96dvh] w-full max-w-2xl flex-col overflow-hidden rounded-xl border border-slate-200 bg-slate-50 shadow-2xl sm:max-h-[92dvh] sm:rounded-2xl"
      >
        <header className="flex shrink-0 items-center justify-between gap-4 border-b border-slate-200 bg-white px-4 py-3 sm:px-7 sm:py-4">
          <div>
            <h2
              id="titulo-nueva-solicitud"
              className="text-lg font-bold text-slate-900 sm:text-xl"
            >
              Nueva solicitud
            </h2>

            <p className="mt-1 text-xs text-slate-500 sm:text-sm">
              Cuéntanos qué problema o requerimiento necesitas reportar.
            </p>
          </div>

          <button
            type="button"
            onClick={onCerrar}
            aria-label="Cerrar formulario"
            className="shrink-0 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-lg text-slate-600 hover:bg-slate-100"
          >
            ×
          </button>
        </header>

        <form
          onSubmit={enviarFormulario}
          className="flex min-h-0 flex-1 flex-col"
        >
          <div className="min-h-0 flex-1 space-y-4 overflow-y-auto overscroll-contain p-4 sm:space-y-5 sm:p-7">
            {error && <MensajeEstado tipo="error" mensaje={error} />}

            <div>
              <label htmlFor="titulo" className={ETIQUETA}>
                Título de la solicitud *
              </label>

              <input
                id="titulo"
                required
                maxLength={200}
                value={formulario.titulo}
                onChange={(e) => actualizar('titulo', e.target.value)}
                placeholder="Ej. No funciona mi computador"
                className={CAMPO}
              />
            </div>

            <div>
              <label htmlFor="descripcion" className={ETIQUETA}>
                Descripción del problema *
              </label>

              <textarea
                id="descripcion"
                required
                maxLength={5000}
                rows={3}
                value={formulario.descripcion}
                onChange={(e) => actualizar('descripcion', e.target.value)}
                placeholder="Describe detalladamente lo que sucede..."
                className={`${CAMPO} resize-y`}
              />
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="tipo" className={ETIQUETA}>
                  Tipo de solicitud *
                </label>

                <select
                  id="tipo"
                  value={formulario.tipo}
                  onChange={(e) =>
                    actualizar('tipo', e.target.value as TipoSolicitud)
                  }
                  className={CAMPO}
                >
                  <option value="incidente">Incidente</option>
                  <option value="requerimiento">Requerimiento</option>
                </select>
              </div>

              <div>
                <label htmlFor="categoria" className={ETIQUETA}>
                  Categoría
                </label>

                <select
                  id="categoria"
                  value={formulario.categoria_id}
                  onChange={(e) => actualizar('categoria_id', e.target.value)}
                  disabled={cargandoCategorias}
                  className={CAMPO}
                >
                  <option value="">
                    {cargandoCategorias
                      ? 'Cargando categorías...'
                      : 'Seleccionar categoría'}
                  </option>

                  {categorias.map((categoria) => (
                    <option key={categoria.id} value={categoria.id}>
                      {categoria.nombre}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="ubicacion" className={ETIQUETA}>
                  Ubicación *
                </label>

                <input
                  id="ubicacion"
                  required
                  maxLength={200}
                  value={formulario.ubicacion}
                  onChange={(e) => actualizar('ubicacion', e.target.value)}
                  placeholder="Ej. Bloque A, oficina 203"
                  className={CAMPO}
                />
              </div>

              <div>
                <label htmlFor="placa_equipo" className={ETIQUETA}>
                  Placa del equipo
                </label>

                <input
                  id="placa_equipo"
                  maxLength={50}
                  value={formulario.placa_equipo}
                  onChange={(e) =>
                    actualizar('placa_equipo', e.target.value)
                  }
                  placeholder="Si aplica"
                  className={CAMPO}
                />
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <h3 className="text-sm font-semibold text-slate-800">
                Datos de contacto
              </h3>

              <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label htmlFor="medio_contacto" className={ETIQUETA}>
                    Medio de contacto *
                  </label>

                  <select
                    id="medio_contacto"
                    value={formulario.medio_contacto}
                    onChange={(e) =>
                      actualizar(
                        'medio_contacto',
                        e.target.value as 'correo' | 'telefono',
                      )
                    }
                    className={CAMPO}
                  >
                    <option value="correo">Correo electrónico</option>
                    <option value="telefono">Teléfono</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="dato_contacto" className={ETIQUETA}>
                    {formulario.medio_contacto === 'correo'
                      ? 'Correo electrónico *'
                      : 'Número de teléfono *'}
                  </label>

                  <input
                    id="dato_contacto"
                    required
                    maxLength={255}
                    type={
                      formulario.medio_contacto === 'correo' ? 'email' : 'tel'
                    }
                    value={formulario.dato_contacto}
                    onChange={(e) =>
                      actualizar('dato_contacto', e.target.value)
                    }
                    placeholder={
                      formulario.medio_contacto === 'correo'
                        ? 'nombre@correo.com'
                        : '300 123 4567'
                    }
                    className={CAMPO}
                  />
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-500">
              Los campos marcados con * son obligatorios. La prioridad será
              establecida durante la evaluación de la solicitud.
            </p>
          </div>

          <footer className="flex shrink-0 flex-col-reverse gap-2 border-t border-slate-200 bg-white p-3 sm:flex-row sm:justify-end sm:px-7 sm:py-4">
            <Boton
              variante="secundario"
              onClick={onCerrar}
              disabled={enviando}
            >
              Cancelar
            </Boton>

            <button
              type="submit"
              disabled={enviando}
              className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {enviando ? 'Registrando...' : 'Enviar solicitud'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}

export function SolicitanteDashboardPage() {
  const [resultado, setResultado] = useState<SolicitudesPagina | null>(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [solicitudConversacion, setSolicitudConversacion] =
    useState<SolicitudResumen | null>(null)
  const [recarga, setRecarga] = useState(0)
  const [mensajeExito, setMensajeExito] = useState('')

  useEffect(() => {
    let vigente = true

    setCargando(true)

    api<SolicitudesPagina>('/requests?page=1&limit=100')
      .then((respuesta) => {
        if (!vigente) return

        setResultado(respuesta)
        setError('')
      })
      .catch((err: unknown) => {
        if (!vigente) return

        setError(
          err instanceof Error
            ? err.message
            : 'No fue posible consultar tus solicitudes.',
        )
      })
      .finally(() => {
        if (vigente) setCargando(false)
      })

    return () => {
      vigente = false
    }
  }, [recarga])

  const solicitudesOrdenadas = useMemo(
    () => ordenarSolicitudes(resultado?.data ?? []),
    [resultado],
  )

  function solicitudCreada() {
    setMostrarFormulario(false)
    setMensajeExito('Tu solicitud fue registrada correctamente.')
    setRecarga((actual) => actual + 1)
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Mis casos</h1>

          <p className="mt-1 text-sm text-slate-600">
            Consulta el estado de tus solicitudes de soporte.
          </p>
        </div>

        <Boton
          onClick={() => {
            setMensajeExito('')
            setMostrarFormulario(true)
          }}
        >
          + Nueva solicitud
        </Boton>
      </div>

      {mensajeExito && (
        <div className="rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800">
          {mensajeExito}
        </div>
      )}

      {error && <MensajeEstado tipo="error" mensaje={error} />}

      {cargando ? (
        <Cargando mensaje="Consultando tus solicitudes..." />
      ) : solicitudesOrdenadas.length > 0 ? (
        <div className="space-y-4">
          {solicitudesOrdenadas.map((solicitud) => (
            <TarjetaSolicitud
              key={solicitud.id}
              solicitud={solicitud}
              onVerConversacion={() => setSolicitudConversacion(solicitud)}
            />
          ))}
        </div>
      ) : (
        !error && (
          <div className="rounded-xl border border-slate-200 bg-white px-6 py-12 text-center shadow-sm">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-500">
              <span className="text-xl">+</span>
            </div>

            <h2 className="mt-4 text-lg font-semibold text-slate-900">
              Todavía no tienes casos registrados
            </h2>

            <p className="mt-2 text-sm text-slate-600">
              Cuando registres una solicitud, podrás consultar aquí su estado
              y seguimiento.
            </p>

            <div className="mt-5">
              <Boton onClick={() => setMostrarFormulario(true)}>
                Crear mi primera solicitud
              </Boton>
            </div>
          </div>
        )
      )}

      {mostrarFormulario && (
        <FormularioNuevaSolicitud
          onCerrar={() => setMostrarFormulario(false)}
          onCreada={solicitudCreada}
        />
      )}

      {solicitudConversacion && (
        <ConversacionSolicitud
          solicitud={solicitudConversacion}
          onCerrar={() => setSolicitudConversacion(null)}
        />
      )}
    </section>
  )
}
