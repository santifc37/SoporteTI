
import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { Cargando } from '../../components/Cargando'
import { MensajeEstado } from '../../components/MensajeEstado'
import { AdjuntosSolicitud } from '../../components/coordinador/AdjuntosSolicitud'
import { HistorialCambios } from '../../components/coordinador/HistorialCambios'
import { InsigniaEstado, InsigniaPrioridad } from '../../components/coordinador/Insignias'
import { PanelGestion } from '../../components/coordinador/PanelGestion'
import {
  CLASE_TARJETA,
  NOMBRES_TIPO_CIERRE,
  formatearFecha,
  mensajeDeError,
} from '../../components/coordinador/etiquetas'
import { ConversacionSolicitudTecnico } from '../../components/tecnico/ConversacionSolicitudTecnico'
import {
  consultarAdjuntosSolicitud,
  consultarAsignaciones,
  consultarCategorias,
  consultarHistorial,
  consultarTecnicosActivos,
} from '../../services/coordinador'
import {
  consultarDetalleSolicitud,
  consultarIntervenciones,
  consultarPeticionesInformacion,
} from '../../services/tecnico'

import type {
  Intervencion,
  PeticionInformacion,
  SolicitudDetalle,
} from '../../services/tecnico'
import type {
  AdjuntoSolicitud,
  AsignacionHistorial,
  CambioHistorial,
  Categoria,
  UsuarioListado,
} from '../../types/coordinador'

function Campo({ etiqueta, valor }: { etiqueta: string; valor: string }) {
  return (
    <div>
      <p className="text-xs font-medium text-texto-secundario">{etiqueta}</p>
      <p className="mt-1 break-words text-sm font-medium text-texto">
        {valor || 'No disponible'}
      </p>
    </div>
  )
}

/** Si una consulta secundaria falla, la página sigue mostrando el resto. */
async function oVacio<T>(promesa: Promise<T[]>): Promise<T[]> {
  try {
    return await promesa
  } catch {
    return []
  }
}

export function DetalleSolicitudCoordinadorPage() {
  const { solicitudId } = useParams<{ solicitudId: string }>()

  const [solicitud, setSolicitud] = useState<SolicitudDetalle | null>(null)
  const [adjuntos, setAdjuntos] = useState<AdjuntoSolicitud[]>([])
  const [intervenciones, setIntervenciones] = useState<Intervencion[]>([])
  const [peticiones, setPeticiones] = useState<PeticionInformacion[]>([])
  const [asignaciones, setAsignaciones] = useState<AsignacionHistorial[]>([])
  const [historial, setHistorial] = useState<CambioHistorial[]>([])
  const [categorias, setCategorias] = useState<Categoria[]>([])
  const [tecnicos, setTecnicos] = useState<UsuarioListado[]>([])

  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')

  const cargarDatos = useCallback(async () => {
    if (!solicitudId) return

    try {
      const detalle = await consultarDetalleSolicitud(solicitudId)

      const [
        listaAdjuntos,
        listaIntervenciones,
        listaPeticiones,
        listaAsignaciones,
        listaHistorial,
      ] = await Promise.all([
        oVacio(consultarAdjuntosSolicitud(solicitudId)),
        oVacio(consultarIntervenciones(solicitudId).then((r) => r.data)),
        oVacio(consultarPeticionesInformacion(solicitudId).then((r) => r.data)),
        oVacio(consultarAsignaciones(solicitudId)),
        oVacio(consultarHistorial(solicitudId).then((r) => r.data)),
      ])

      setSolicitud(detalle)
      setAdjuntos(listaAdjuntos)
      setIntervenciones(listaIntervenciones)
      setPeticiones(listaPeticiones)
      setAsignaciones(listaAsignaciones)
      setHistorial(listaHistorial)
    } catch (err) {
      setError(mensajeDeError(err, 'No fue posible consultar la solicitud.'))
    } finally {
      setCargando(false)
    }
  }, [solicitudId])

  useEffect(() => {
    void cargarDatos()
  }, [cargarDatos])

  // Opciones de la gestión: categorías (incluye inactivas) y técnicos activos.
  useEffect(() => {
    consultarCategorias({ limit: 100 })
      .then((respuesta) => setCategorias(respuesta.data))
      .catch(() => setCategorias([]))

    consultarTecnicosActivos()
      .then(setTecnicos)
      .catch(() => setTecnicos([]))
  }, [])

  async function alTerminarAccion(texto: string) {
    setError('')
    setMensaje(texto)
    await cargarDatos()
  }

  function alFallarAccion(texto: string) {
    setMensaje('')
    setError(texto)
  }

  if (cargando) {
    return <Cargando mensaje="Cargando detalle de la solicitud..." />
  }

  if (!solicitud) {
    return (
      <section className="space-y-4">
        <Link to="/coordinador" className="text-sm font-medium text-accion hover:underline">
          ← Volver a la bandeja
        </Link>
        <MensajeEstado tipo="error" mensaje={error || 'No se encontró la solicitud.'} />
      </section>
    )
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <Link to="/coordinador" className="text-sm font-medium text-accion hover:underline">
            ← Volver a la bandeja
          </Link>
          <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-texto-secundario">
            {solicitud.numero} · <span className="capitalize">{solicitud.tipo}</span>
          </p>
          <h1 className="mt-1 text-2xl font-bold text-texto">{solicitud.titulo}</h1>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <InsigniaPrioridad prioridad={solicitud.prioridad} />
          <InsigniaEstado estado={solicitud.estado} grande />
        </div>
      </div>

      {error && <MensajeEstado tipo="error" mensaje={error} />}
      {mensaje && <MensajeEstado tipo="exito" mensaje={mensaje} />}

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_380px]">
        {/* Columna principal: información del caso y seguimiento */}
        <div className="min-w-0 space-y-6">
          <div className={CLASE_TARJETA}>
            <h2 className="text-lg font-semibold text-texto">Información del caso</h2>

            <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-texto">
              {solicitud.descripcion}
            </p>

            <div className="mt-6 grid gap-5 border-t border-panel pt-5 sm:grid-cols-2 lg:grid-cols-3">
              <Campo etiqueta="Solicitante" valor={solicitud.solicitante?.nombre ?? ''} />
              <Campo etiqueta="Categoría" valor={solicitud.categoria?.nombre ?? 'Sin categoría'} />
              <Campo etiqueta="Técnico asignado" valor={solicitud.tecnico_asignado?.nombre ?? 'Sin asignar'} />
              <Campo etiqueta="Ubicación" valor={solicitud.ubicacion} />
              <Campo etiqueta="Placa del equipo" valor={solicitud.placa_equipo ?? 'No aplica'} />
              <Campo etiqueta="Medio de contacto" valor={`${solicitud.medio_contacto}: ${solicitud.dato_contacto}`} />
              <Campo etiqueta="Fecha de creación" valor={formatearFecha(solicitud.fecha_creacion)} />
              <Campo etiqueta="Última actualización" valor={formatearFecha(solicitud.fecha_actualizacion)} />
              {solicitud.fecha_cierre && (
                <Campo etiqueta="Fecha de cierre" valor={formatearFecha(solicitud.fecha_cierre)} />
              )}
            </div>

            {solicitud.solucion_final && (
              <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
                <h3 className="font-semibold text-emerald-900">Solución registrada</h3>
                <p className="mt-2 whitespace-pre-wrap text-sm text-emerald-900">
                  {solicitud.solucion_final}
                </p>
                {solicitud.fecha_resolucion && (
                  <p className="mt-2 text-xs text-emerald-800">
                    {formatearFecha(solicitud.fecha_resolucion)}
                  </p>
                )}
              </div>
            )}

            {solicitud.tipo_cierre && (
              <div className="mt-4 rounded-lg border border-panel bg-fondo p-4">
                <h3 className="font-semibold text-texto">
                  Cierre: {NOMBRES_TIPO_CIERRE[solicitud.tipo_cierre] ?? solicitud.tipo_cierre}
                </h3>
                {solicitud.motivo_cierre && (
                  <p className="mt-2 whitespace-pre-wrap text-sm text-texto-secundario">
                    {solicitud.motivo_cierre}
                  </p>
                )}
              </div>
            )}
          </div>

          <AdjuntosSolicitud adjuntos={adjuntos} />

          <ConversacionSolicitudTecnico solicitud={solicitud} />

          <div className={CLASE_TARJETA}>
            <h2 className="text-lg font-semibold text-texto">Intervenciones</h2>
            <p className="mt-1 text-sm text-texto-secundario">
              Trabajo registrado por los técnicos, incluidas las notas internas.
            </p>

            {intervenciones.length > 0 ? (
              <div className="mt-5 space-y-4">
                {intervenciones.map((intervencion) => (
                  <article key={intervencion.id} className="rounded-lg border border-panel bg-fondo p-4">
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
                        {intervencion.visibilidad === 'interna' ? 'Nota interna' : 'Visible para solicitante'}
                      </span>
                    </div>

                    <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-texto">
                      {intervencion.descripcion}
                    </p>

                    {intervencion.diagnostico && (
                      <div className="mt-3 rounded-md bg-tarjeta p-3">
                        <p className="text-xs font-semibold text-texto-secundario">Diagnóstico</p>
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

          <div className={CLASE_TARJETA}>
            <h2 className="text-lg font-semibold text-texto">Solicitudes de información</h2>
            <p className="mt-1 text-sm text-texto-secundario">
              Datos que el técnico pidió al solicitante y sus respuestas.
            </p>

            {peticiones.length > 0 ? (
              <div className="mt-5 space-y-4">
                {peticiones.map((peticion) => (
                  <article key={peticion.id} className="rounded-lg border border-panel bg-fondo p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <p className="text-sm font-semibold text-texto">
                        {peticion.solicitado_por.nombre}
                      </p>
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                          peticion.respuesta
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {peticion.respuesta ? 'Respondida' : 'Pendiente de respuesta'}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-texto-secundario">
                      {formatearFecha(peticion.fecha_solicitud)}
                    </p>
                    <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-texto">
                      {peticion.contenido}
                    </p>

                    {peticion.respuesta && (
                      <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-3">
                        <p className="text-xs font-semibold uppercase text-emerald-800">
                          Respuesta del solicitante
                        </p>
                        <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-emerald-900">
                          {peticion.respuesta.contenido}
                        </p>
                      </div>
                    )}
                  </article>
                ))}
              </div>
            ) : (
              <p className="mt-5 rounded-lg bg-fondo p-5 text-center text-sm text-texto-secundario">
                No se ha pedido información adicional en este caso.
              </p>
            )}
          </div>
        </div>

        {/* Columna lateral: acciones del coordinador y trazabilidad */}
        <aside className="min-w-0 space-y-6">
          <PanelGestion
            key={solicitud.fecha_actualizacion}
            solicitud={solicitud}
            categorias={categorias}
            tecnicos={tecnicos}
            onExito={alTerminarAccion}
            onError={alFallarAccion}
          />

          <div className={CLASE_TARJETA}>
            <h2 className="text-lg font-semibold text-texto">Asignaciones</h2>
            {asignaciones.length > 0 ? (
              <ul className="mt-4 space-y-3">
                {asignaciones.map((asignacion) => (
                  <li key={asignacion.id} className="rounded-lg border border-panel bg-fondo p-3">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-semibold text-texto">{asignacion.tecnico_nombre}</p>
                      {!asignacion.fecha_finalizacion && (
                        <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-800">
                          Actual
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-xs text-texto-secundario">
                      {formatearFecha(asignacion.fecha_asignacion)}
                      {asignacion.fecha_finalizacion &&
                        ` — ${formatearFecha(asignacion.fecha_finalizacion)}`}
                    </p>
                    {asignacion.observacion && (
                      <p className="mt-2 whitespace-pre-wrap text-sm text-texto">{asignacion.observacion}</p>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-4 text-sm text-texto-secundario">Todavía no se ha asignado un técnico.</p>
            )}
          </div>

          <HistorialCambios cambios={historial} />
        </aside>
      </div>
    </section>
  )
}
