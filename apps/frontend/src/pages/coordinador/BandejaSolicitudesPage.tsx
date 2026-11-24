
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { Boton } from '../../components/Boton'
import { Cargando } from '../../components/Cargando'
import { MensajeEstado } from '../../components/MensajeEstado'
import { InsigniaEstado, InsigniaPrioridad } from '../../components/coordinador/Insignias'
import { Paginacion } from '../../components/coordinador/Paginacion'
import {
  CLASE_CAMPO,
  CLASE_TARJETA,
  ESTADOS,
  PRIORIDADES,
  formatearFecha,
  mensajeDeError,
} from '../../components/coordinador/etiquetas'
import {
  consultarCategorias,
  consultarSolicitudes,
  consultarTecnicosActivos,
} from '../../services/coordinador'

import type { Categoria, FiltrosCoordinador, UsuarioListado } from '../../types/coordinador'
import type {
  EstadoSolicitud,
  PrioridadSolicitud,
  SolicitudResumen,
  SolicitudesPagina,
  TipoSolicitud,
} from '../../types/solicitud'

/** Atajos de la bandeja: muestran primero lo que necesita una acción del coordinador. */
const ATAJOS: { nombre: string; estado: EstadoSolicitud | '' }[] = [
  { nombre: 'Todas', estado: '' },
  { nombre: 'Por evaluar', estado: 'registrado' },
  { nombre: 'En evaluación', estado: 'en_evaluacion' },
  { nombre: 'Resueltas por cerrar', estado: 'resuelto' },
]

function FilaSolicitud({ solicitud }: { solicitud: SolicitudResumen }) {
  return (
    <article className="rounded-xl border border-panel bg-tarjeta p-5 shadow-sm transition hover:border-blue-300 hover:shadow-md">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide text-texto-secundario">
            {solicitud.numero} · <span className="capitalize">{solicitud.tipo}</span>
          </p>
          <h3 className="mt-1 break-words text-base font-semibold text-texto">
            {solicitud.titulo}
          </h3>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <InsigniaPrioridad prioridad={solicitud.prioridad} />
          <InsigniaEstado estado={solicitud.estado} />
        </div>
      </div>

      <div className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <p className="text-xs text-texto-secundario">Solicitante</p>
          <p className="mt-1 font-medium text-texto">
            {solicitud.solicitante?.nombre ?? 'No disponible'}
          </p>
        </div>

        <div>
          <p className="text-xs text-texto-secundario">Categoría</p>
          <p className="mt-1 font-medium text-texto">
            {solicitud.categoria?.nombre ?? 'Sin categoría'}
          </p>
        </div>

        <div>
          <p className="text-xs text-texto-secundario">Técnico asignado</p>
          <p className="mt-1 font-medium text-texto">
            {solicitud.tecnico_asignado?.nombre ?? 'Sin asignar'}
          </p>
        </div>

        <div>
          <p className="text-xs text-texto-secundario">Fecha de creación</p>
          <p className="mt-1 font-medium text-texto">
            {formatearFecha(solicitud.fecha_creacion)}
          </p>
        </div>
      </div>

      <div className="mt-5 flex justify-end border-t border-panel pt-4">
        <Link
          to={`/coordinador/solicitud/${solicitud.id}`}
          className="inline-flex items-center gap-2 rounded-lg bg-primario px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-accion"
        >
          Gestionar
          <span aria-hidden="true">→</span>
        </Link>
      </div>
    </article>
  )
}

export function BandejaSolicitudesPage() {
  const [resultado, setResultado] = useState<SolicitudesPagina | null>(null)
  const [categorias, setCategorias] = useState<Categoria[]>([])
  const [tecnicos, setTecnicos] = useState<UsuarioListado[]>([])

  const [busqueda, setBusqueda] = useState('')
  const [estado, setEstado] = useState('')
  const [prioridad, setPrioridad] = useState('')
  const [tipo, setTipo] = useState('')
  const [categoriaId, setCategoriaId] = useState('')
  const [tecnicoId, setTecnicoId] = useState('')
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  const [pagina, setPagina] = useState(1)

  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [recarga, setRecarga] = useState(0)

  // Opciones de los filtros: se cargan una sola vez.
  useEffect(() => {
    consultarCategorias({ limit: 100 })
      .then((respuesta) => setCategorias(respuesta.data))
      .catch(() => setCategorias([]))

    consultarTecnicosActivos()
      .then(setTecnicos)
      .catch(() => setTecnicos([]))
  }, [])

  useEffect(() => {
    let vigente = true

    const filtros: FiltrosCoordinador = {
      page: pagina,
      limit: 20,
      busqueda: busqueda.trim() || undefined,
      estado: (estado || undefined) as EstadoSolicitud | undefined,
      prioridad: (prioridad || undefined) as PrioridadSolicitud | undefined,
      tipo: (tipo || undefined) as TipoSolicitud | undefined,
      categoria_id: categoriaId || undefined,
      tecnico_id: tecnicoId || undefined,
      fecha_desde: fechaDesde || undefined,
      fecha_hasta: fechaHasta || undefined,
    }

    consultarSolicitudes(filtros)
      .then((respuesta) => {
        if (!vigente) return
        setResultado(respuesta)
        setError('')
      })
      .catch((err: unknown) => {
        if (!vigente) return
        setError(mensajeDeError(err, 'No fue posible consultar las solicitudes.'))
        setResultado(null)
      })
      .finally(() => {
        if (vigente) setCargando(false)
      })

    return () => {
      vigente = false
    }
  }, [busqueda, estado, prioridad, tipo, categoriaId, tecnicoId, fechaDesde, fechaHasta, pagina, recarga])

  function limpiarFiltros() {
    setBusqueda('')
    setEstado('')
    setPrioridad('')
    setTipo('')
    setCategoriaId('')
    setTecnicoId('')
    setFechaDesde('')
    setFechaHasta('')
    setPagina(1)
  }

  // Envuelve un setter para que cualquier cambio de filtro vuelva a la página 1.
  function alCambiar(setter: (valor: string) => void) {
    return (valor: string) => {
      setter(valor)
      setPagina(1)
    }
  }

  const totalPaginas = resultado?.pagination.total_pages ?? 0
  const totalSolicitudes = resultado?.pagination.total ?? 0

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-texto">
          Bandeja de solicitudes
        </h1>
        <p className="mt-1 text-sm text-texto-secundario">
          Evalúa, clasifica, asigna y cierra las solicitudes de la organización.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {ATAJOS.map((atajo) => (
          <button
            key={atajo.nombre}
            type="button"
            onClick={() => alCambiar(setEstado)(atajo.estado)}
            className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
              estado === atajo.estado
                ? 'bg-primario text-white shadow-sm'
                : 'border border-panel bg-tarjeta text-texto hover:bg-panel'
            }`}
          >
            {atajo.nombre}
          </button>
        ))}
      </div>

      <div className={CLASE_TARJETA}>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <label htmlFor="busqueda" className="mb-1 block text-sm font-medium text-texto">
              Buscar
            </label>
            <input
              id="busqueda"
              type="search"
              value={busqueda}
              onChange={(evento) => alCambiar(setBusqueda)(evento.target.value)}
              placeholder="Número o título..."
              className={CLASE_CAMPO}
            />
          </div>

          <div>
            <label htmlFor="estado" className="mb-1 block text-sm font-medium text-texto">
              Estado
            </label>
            <select
              id="estado"
              value={estado}
              onChange={(evento) => alCambiar(setEstado)(evento.target.value)}
              className={CLASE_CAMPO}
            >
              <option value="">Todos los estados</option>
              {ESTADOS.map((opcion) => (
                <option key={opcion.valor} value={opcion.valor}>
                  {opcion.nombre}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="prioridad" className="mb-1 block text-sm font-medium text-texto">
              Prioridad
            </label>
            <select
              id="prioridad"
              value={prioridad}
              onChange={(evento) => alCambiar(setPrioridad)(evento.target.value)}
              className={CLASE_CAMPO}
            >
              <option value="">Todas las prioridades</option>
              {PRIORIDADES.map((opcion) => (
                <option key={opcion.valor} value={opcion.valor}>
                  {opcion.nombre}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="tipo" className="mb-1 block text-sm font-medium text-texto">
              Tipo de solicitud
            </label>
            <select
              id="tipo"
              value={tipo}
              onChange={(evento) => alCambiar(setTipo)(evento.target.value)}
              className={CLASE_CAMPO}
            >
              <option value="">Todos los tipos</option>
              <option value="incidente">Incidente</option>
              <option value="requerimiento">Requerimiento</option>
            </select>
          </div>

          <div>
            <label htmlFor="categoria" className="mb-1 block text-sm font-medium text-texto">
              Categoría
            </label>
            <select
              id="categoria"
              value={categoriaId}
              onChange={(evento) => alCambiar(setCategoriaId)(evento.target.value)}
              className={CLASE_CAMPO}
            >
              <option value="">Todas las categorías</option>
              {categorias.map((categoria) => (
                <option key={categoria.id} value={categoria.id}>
                  {categoria.nombre}
                  {categoria.activa ? '' : ' (inactiva)'}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="tecnico" className="mb-1 block text-sm font-medium text-texto">
              Técnico
            </label>
            <select
              id="tecnico"
              value={tecnicoId}
              onChange={(evento) => alCambiar(setTecnicoId)(evento.target.value)}
              className={CLASE_CAMPO}
            >
              <option value="">Todos los técnicos</option>
              {tecnicos.map((tecnico) => (
                <option key={tecnico.id} value={tecnico.id}>
                  {tecnico.nombre} {tecnico.apellido}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="fecha-desde" className="mb-1 block text-sm font-medium text-texto">
              Creada desde
            </label>
            <input
              id="fecha-desde"
              type="date"
              value={fechaDesde}
              max={fechaHasta || undefined}
              onChange={(evento) => alCambiar(setFechaDesde)(evento.target.value)}
              className={CLASE_CAMPO}
            />
          </div>

          <div>
            <label htmlFor="fecha-hasta" className="mb-1 block text-sm font-medium text-texto">
              Creada hasta
            </label>
            <input
              id="fecha-hasta"
              type="date"
              value={fechaHasta}
              min={fechaDesde || undefined}
              onChange={(evento) => alCambiar(setFechaHasta)(evento.target.value)}
              className={CLASE_CAMPO}
            />
          </div>
        </div>

        <div className="mt-4 flex flex-wrap justify-end gap-2">
          <Boton variante="secundario" onClick={limpiarFiltros}>
            Limpiar filtros
          </Boton>
          <Boton
            variante="secundario"
            onClick={() => setRecarga((actual) => actual + 1)}
          >
            Actualizar
          </Boton>
        </div>
      </div>

      {error && <MensajeEstado tipo="error" mensaje={error} />}

      {cargando ? (
        <Cargando mensaje="Consultando solicitudes..." />
      ) : (
        <>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm text-texto-secundario">
              {totalSolicitudes}{' '}
              {totalSolicitudes === 1 ? 'solicitud encontrada' : 'solicitudes encontradas'}
            </p>
            {totalPaginas > 0 && (
              <p className="text-sm text-texto-secundario">
                Página {pagina} de {totalPaginas}
              </p>
            )}
          </div>

          {resultado && resultado.data.length > 0 ? (
            <div className="space-y-4">
              {resultado.data.map((solicitud) => (
                <FilaSolicitud key={solicitud.id} solicitud={solicitud} />
              ))}
            </div>
          ) : (
            !error && (
              <div className="rounded-xl border border-panel bg-tarjeta px-6 py-12 text-center">
                <h2 className="text-lg font-semibold text-texto">
                  No hay solicitudes
                </h2>
                <p className="mt-2 text-sm text-texto-secundario">
                  No se encontraron solicitudes con los filtros seleccionados.
                </p>
              </div>
            )
          )}

          <Paginacion
            pagina={pagina}
            totalPaginas={totalPaginas}
            onCambiar={setPagina}
          />
        </>
      )}
    </section>
  )
}
