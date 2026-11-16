
import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { Boton } from '../../components/Boton'
import { Cargando } from '../../components/Cargando'
import { MensajeEstado } from '../../components/MensajeEstado'

import {
  actualizarEstadoSolicitud,
  adjuntarImagenIntervencion,
  consultarDetalleSolicitud,
  consultarIntervenciones,
  registrarIntervencion,
  registrarSolucion,
  solicitarInformacion,
} from '../../services/tecnico'

import type {
  Intervencion,
  SolicitudDetalle,
} from '../../services/tecnico'

const NOMBRES_ESTADO: Record<string, string> = {
  registrado: 'Registrado',
  en_evaluacion: 'En evaluación',
  asignado: 'Asignado',
  en_atencion: 'En atención',
  en_espera: 'En espera',
  resuelto: 'Resuelto',
  cerrado: 'Cerrado',
}

const ESTILOS_ESTADO: Record<string, string> = {
  registrado: 'bg-panel text-texto-secundario',
  en_evaluacion: 'bg-blue-100 text-blue-800',
  asignado: 'bg-indigo-100 text-indigo-800',
  en_atencion: 'bg-amber-100 text-amber-800',
  en_espera: 'bg-orange-100 text-orange-800',
  resuelto: 'bg-emerald-100 text-emerald-800',
  cerrado: 'bg-slate-200 text-slate-700',
}

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

function Campo({
  etiqueta,
  valor,
}: {
  etiqueta: string
  valor: string
}) {
  return (
    <div>
      <p className="text-xs font-medium text-texto-secundario">
        {etiqueta}
      </p>
      <p className="mt-1 break-words text-sm font-medium text-texto">
        {valor || 'No disponible'}
      </p>
    </div>
  )
}

export function DetalleSolicitudTecnicoPage() {
  const { solicitudId } = useParams<{ solicitudId: string }>()
  const navegar = useNavigate()

  const [solicitud, setSolicitud] = useState<SolicitudDetalle | null>(null)
  const [intervenciones, setIntervenciones] = useState<Intervencion[]>([])
  const [cargando, setCargando] = useState(true)
  const [procesando, setProcesando] = useState(false)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')

  const [descripcion, setDescripcion] = useState('')
  const [diagnostico, setDiagnostico] = useState('')
  const [visibilidad, setVisibilidad] = useState<'interna' | 'solicitante'>('interna')
  const [imagen, setImagen] = useState<File | null>(null)

  const [solicitudInformacion, setSolicitudInformacion] = useState('')
  const [solucion, setSolucion] = useState('')

  const cargarDatos = useCallback(async () => {
    if (!solicitudId) return

    setCargando(true)
    setError('')

    try {
      const [detalle, historial] = await Promise.all([
        consultarDetalleSolicitud(solicitudId),
        consultarIntervenciones(solicitudId),
      ])

      setSolicitud(detalle)
      setIntervenciones(historial.data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible consultar la solicitud.',
      )
    } finally {
      setCargando(false)
    }
  }, [solicitudId])

  useEffect(() => {
    void cargarDatos()
  }, [cargarDatos])

  async function cambiarEstado(
    nuevoEstado: 'en_atencion' | 'en_espera',
  ) {
    if (!solicitudId) return

    setProcesando(true)
    setError('')
    setMensaje('')

    try {
      await actualizarEstadoSolicitud(solicitudId, nuevoEstado)
      setMensaje('El estado de la solicitud se actualizó correctamente.')
      await cargarDatos()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible actualizar el estado.',
      )
    } finally {
      setProcesando(false)
    }
  }

  async function guardarIntervencion(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    if (!solicitudId || !descripcion.trim()) return

    setProcesando(true)
    setError('')
    setMensaje('')

    try {
      const nuevaIntervencion = await registrarIntervencion(
        solicitudId,
        {
          descripcion: descripcion.trim(),
          diagnostico: diagnostico.trim(),
          visibilidad,
        },
      )

      if (imagen) {
        try {
          await adjuntarImagenIntervencion(
            solicitudId,
            nuevaIntervencion.id,
            imagen,
          )
        } catch (err) {
          setMensaje(
            'La intervención se guardó, pero no fue posible adjuntar la imagen.',
          )
          setError(
            err instanceof Error
              ? err.message
              : 'Error al adjuntar la imagen.',
          )
          setDescripcion('')
          setDiagnostico('')
          setImagen(null)
          await cargarDatos()
          return
        }
      }

      setDescripcion('')
      setDiagnostico('')
      setVisibilidad('interna')
      setImagen(null)
      setMensaje('La intervención se registró correctamente.')
      await cargarDatos()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible registrar la intervención.',
      )
    } finally {
      setProcesando(false)
    }
  }

  async function enviarSolicitudInformacion(
    evento: FormEvent<HTMLFormElement>,
  ) {
    evento.preventDefault()

    if (!solicitudId || !solicitudInformacion.trim()) return

    setProcesando(true)
    setError('')
    setMensaje('')

    try {
      await solicitarInformacion(
        solicitudId,
        solicitudInformacion.trim(),
      )

      setSolicitudInformacion('')
      setMensaje('La solicitud de información se envió correctamente.')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible solicitar la información.',
      )
    } finally {
      setProcesando(false)
    }
  }

  async function resolverSolicitud(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    if (!solicitudId || !solucion.trim()) return

    const confirmar = window.confirm(
      '¿Confirmas que deseas registrar la solución de esta solicitud?',
    )

    if (!confirmar) return

    setProcesando(true)
    setError('')
    setMensaje('')

    try {
      await registrarSolucion(solicitudId, solucion.trim())
      setSolucion('')
      setMensaje('La solución se registró correctamente.')
      await cargarDatos()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible registrar la solución.',
      )
    } finally {
      setProcesando(false)
    }
  }

  if (cargando) {
    return <Cargando mensaje="Cargando detalle de la solicitud..." />
  }

  if (!solicitud) {
    return (
      <section className="space-y-4">
        <Boton
          variante="secundario"
          onClick={() => navegar('/tecnico')}
        >
          Volver a solicitudes
        </Boton>

        <MensajeEstado
          tipo="error"
          mensaje={error || 'No se encontró la solicitud.'}
        />
      </section>
    )
  }

  const finalizada =
    solicitud.estado === 'resuelto' || solicitud.estado === 'cerrado'

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Link
            to="/tecnico"
            className="text-sm font-medium text-accion hover:underline"
          >
            ← Volver a solicitudes
          </Link>

          <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-texto-secundario">
            {solicitud.numero}
          </p>

          <h1 className="mt-1 text-2xl font-bold text-texto">
            {solicitud.titulo}
          </h1>
        </div>

        <span
          className={`rounded-full px-3 py-1.5 text-sm font-semibold ${
            ESTILOS_ESTADO[solicitud.estado] ?? 'bg-panel text-texto'
          }`}
        >
          {NOMBRES_ESTADO[solicitud.estado] ?? solicitud.estado}
        </span>
      </div>

      {error && <MensajeEstado tipo="error" mensaje={error} />}
      {mensaje && <MensajeEstado tipo="exito" mensaje={mensaje} />}

      <div className="rounded-xl border border-panel bg-tarjeta p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-texto">
              Gestión de la solicitud
            </h2>
            <p className="mt-1 text-sm text-texto-secundario">
              Administra el estado de atención del caso.
            </p>
          </div>

          {!finalizada && (
            <div className="flex flex-wrap gap-2">
              {solicitud.estado === 'asignado' && (
                <Boton
                  disabled={procesando}
                  onClick={() => void cambiarEstado('en_atencion')}
                >
                  Iniciar atención
                </Boton>
              )}

              {solicitud.estado === 'en_atencion' && (
                <Boton
                  variante="secundario"
                  disabled={procesando}
                  onClick={() => void cambiarEstado('en_espera')}
                >
                  Poner en espera
                </Boton>
              )}

              {solicitud.estado === 'en_espera' && (
                <Boton
                  disabled={procesando}
                  onClick={() => void cambiarEstado('en_atencion')}
                >
                  Reanudar atención
                </Boton>
              )}
            </div>
          )}
        </div>

        {finalizada && (
          <p className="mt-4 rounded-lg bg-panel p-3 text-sm text-texto-secundario">
            Esta solicitud ya fue finalizada. Puedes consultar su información
            y el historial de intervenciones.
          </p>
        )}
      </div>

      <div className="rounded-xl border border-panel bg-tarjeta p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-texto">
          Información del caso
        </h2>

        <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-texto">
          {solicitud.descripcion}
        </p>

        <div className="mt-6 grid gap-5 border-t border-panel pt-5 sm:grid-cols-2 lg:grid-cols-3">
          <Campo
            etiqueta="Solicitante"
            valor={solicitud.solicitante?.nombre ?? ''}
          />
          <Campo
            etiqueta="Categoría"
            valor={solicitud.categoria?.nombre ?? 'Sin categoría'}
          />
          <Campo
            etiqueta="Tipo"
            valor={solicitud.tipo}
          />
          <Campo
            etiqueta="Prioridad"
            valor={solicitud.prioridad ?? 'No definida'}
          />
          <Campo
            etiqueta="Ubicación"
            valor={solicitud.ubicacion}
          />
          <Campo
            etiqueta="Placa del equipo"
            valor={solicitud.placa_equipo ?? 'No aplica'}
          />
          <Campo
            etiqueta="Medio de contacto"
            valor={solicitud.medio_contacto}
          />
          <Campo
            etiqueta="Dato de contacto"
            valor={solicitud.dato_contacto}
          />
          <Campo
            etiqueta="Fecha de creación"
            valor={formatearFecha(solicitud.fecha_creacion)}
          />
          <Campo
            etiqueta="Técnico asignado"
            valor={solicitud.tecnico_asignado?.nombre ?? 'Sin asignar'}
          />
        </div>

        {solicitud.solucion_final && (
          <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h3 className="font-semibold text-emerald-900">
              Solución registrada
            </h3>
            <p className="mt-2 whitespace-pre-wrap text-sm text-emerald-900">
              {solicitud.solucion_final}
            </p>
          </div>
        )}

        {solicitud.motivo_cierre && (
          <div className="mt-4 rounded-lg border border-panel bg-fondo p-4">
            <h3 className="font-semibold text-texto">
              Motivo de cierre
            </h3>
            <p className="mt-2 whitespace-pre-wrap text-sm text-texto-secundario">
              {solicitud.motivo_cierre}
            </p>
          </div>
        )}
      </div>

      <div className="rounded-xl border border-panel bg-tarjeta p-5 shadow-sm">
        <div>
          <h2 className="text-lg font-semibold text-texto">
            Historial de intervenciones
          </h2>
          <p className="mt-1 text-sm text-texto-secundario">
            Registro de las actividades realizadas sobre este caso.
          </p>
        </div>

        {intervenciones.length > 0 ? (
          <div className="mt-5 space-y-4">
            {intervenciones.map((intervencion) => (
              <article
                key={intervencion.id}
                className="rounded-lg border border-panel bg-fondo p-4"
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-texto">
                      {intervencion.tecnico_nombre ?? 'Técnico'}
                    </p>
                    <p className="mt-1 text-xs text-texto-secundario">
                      {formatearFecha(intervencion.fecha_registro)}
                    </p>
                  </div>

                  <span
                    className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                      intervencion.visibilidad === 'interna'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}
                  >
                    {intervencion.visibilidad === 'interna'
                      ? 'Nota interna'
                      : 'Visible para solicitante'}
                  </span>
                </div>

                <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-texto">
                  {intervencion.descripcion}
                </p>

                {intervencion.diagnostico && (
                  <div className="mt-3 rounded-md bg-tarjeta p-3">
                    <p className="text-xs font-semibold text-texto-secundario">
                      Diagnóstico
                    </p>
                    <p className="mt-1 whitespace-pre-wrap text-sm text-texto">
                      {intervencion.diagnostico}
                    </p>
                  </div>
                )}
              </article>
            ))}
          </div>
        ) : (
          <p className="mt-5 rounded-lg bg-fondo p-5 text-center text-sm text-texto-secundario">
            Todavía no hay intervenciones registradas.
          </p>
        )}
      </div>

      {!finalizada && (
        <>
          <div className="rounded-xl border border-panel bg-tarjeta p-5 shadow-sm">
            <h2 className="text-lg font-semibold text-texto">
              Registrar intervención
            </h2>
            <p className="mt-1 text-sm text-texto-secundario">
              Documenta el trabajo realizado en esta solicitud.
            </p>

            <form
              onSubmit={guardarIntervencion}
              className="mt-5 space-y-4"
            >
              <div>
                <label
                  htmlFor="descripcion-intervencion"
                  className="mb-1 block text-sm font-medium text-texto"
                >
                  Descripción de la intervención
                </label>
                <textarea
                  id="descripcion-intervencion"
                  required
                  rows={4}
                  value={descripcion}
                  onChange={(evento) => setDescripcion(evento.target.value)}
                  placeholder="Describe las actividades realizadas..."
                  className="w-full rounded-lg border border-panel bg-fondo px-3 py-2 text-sm text-texto outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                />
              </div>

              <div>
                <label
                  htmlFor="diagnostico-intervencion"
                  className="mb-1 block text-sm font-medium text-texto"
                >
                  Diagnóstico (opcional)
                </label>
                <textarea
                  id="diagnostico-intervencion"
                  rows={3}
                  value={diagnostico}
                  onChange={(evento) => setDiagnostico(evento.target.value)}
                  placeholder="Describe el diagnóstico técnico..."
                  className="w-full rounded-lg border border-panel bg-fondo px-3 py-2 text-sm text-texto outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                />
              </div>

              <div>
                <label
                  htmlFor="visibilidad-intervencion"
                  className="mb-1 block text-sm font-medium text-texto"
                >
                  Visibilidad
                </label>
                <select
                  id="visibilidad-intervencion"
                  value={visibilidad}
                  onChange={(evento) =>
                    setVisibilidad(evento.target.value as 'interna' | 'solicitante')
                  }
                  className="w-full rounded-lg border border-panel bg-fondo px-3 py-2 text-sm text-texto outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                >
                  <option value="interna">Solo visible para el equipo técnico</option>
                  <option value="solicitante">Visible para el solicitante</option>
                </select>
              </div>

              <div>
                <label
                  htmlFor="imagen-intervencion"
                  className="mb-1 block text-sm font-medium text-texto"
                >
                  Imagen de evidencia (opcional)
                </label>
                <input
                  id="imagen-intervencion"
                  type="file"
                  accept="image/*"
                  onChange={(evento) =>
                    setImagen(evento.target.files?.[0] ?? null)
                  }
                  className="block w-full rounded-lg border border-panel bg-fondo text-sm text-texto file:mr-4 file:border-0 file:bg-panel file:px-4 file:py-2.5 file:font-medium"
                />
                {imagen && (
                  <p className="mt-2 text-xs text-texto-secundario">
                    Archivo seleccionado: {imagen.name}
                  </p>
                )}
              </div>

              <div className="flex justify-end">
                <Boton type="submit" disabled={procesando}>
                  {procesando ? 'Guardando...' : 'Registrar intervención'}
                </Boton>
              </div>
            </form>
          </div>

          <div className="rounded-xl border border-panel bg-tarjeta p-5 shadow-sm">
            <h2 className="text-lg font-semibold text-texto">
              Solicitar información
            </h2>
            <p className="mt-1 text-sm text-texto-secundario">
              Pide al solicitante los datos que hagan falta para continuar.
            </p>

            <form
              onSubmit={enviarSolicitudInformacion}
              className="mt-4 space-y-3"
            >
              <textarea
                required
                rows={3}
                value={solicitudInformacion}
                onChange={(evento) =>
                  setSolicitudInformacion(evento.target.value)
                }
                placeholder="Escribe qué información necesitas..."
                className="w-full rounded-lg border border-panel bg-fondo px-3 py-2 text-sm text-texto outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
              />

              <div className="flex justify-end">
                <Boton
                  type="submit"
                  variante="secundario"
                  disabled={procesando}
                >
                  Enviar solicitud de información
                </Boton>
              </div>
            </form>
          </div>

          <div className="rounded-xl border border-panel bg-tarjeta p-5 shadow-sm">
            <h2 className="text-lg font-semibold text-texto">
              Registrar solución
            </h2>
            <p className="mt-1 text-sm text-texto-secundario">
              Registra la solución aplicada cuando el problema esté resuelto.
            </p>

            <form
              onSubmit={resolverSolicitud}
              className="mt-4 space-y-3"
            >
              <textarea
                required
                rows={4}
                value={solucion}
                onChange={(evento) => setSolucion(evento.target.value)}
                placeholder="Describe la solución aplicada..."
                className="w-full rounded-lg border border-panel bg-fondo px-3 py-2 text-sm text-texto outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
              />

              <div className="flex justify-end">
                <Boton type="submit" disabled={procesando}>
                  Registrar solución y finalizar
                </Boton>
              </div>
            </form>
          </div>
        </>
      )}
    </section>
  )
}
