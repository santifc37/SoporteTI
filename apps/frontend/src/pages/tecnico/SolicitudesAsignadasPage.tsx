
import { useEffect, useState } from 'react'

import { Boton } from '../../components/Boton'
import { Cargando } from '../../components/Cargando'
import { MensajeEstado } from '../../components/MensajeEstado'
import { consultarSolicitudesAsignadas } from '../../services/solicitudes'

import type {
  EstadoSolicitud,
  FiltrosSolicitudes,
  PrioridadSolicitud,
  SolicitudResumen,
  SolicitudesPagina,
} from '../../types/solicitud'

const ESTADOS = [
  { valor: 'asignado', nombre: 'Asignado' },
  { valor: 'en_atencion', nombre: 'En atención' },
  { valor: 'en_espera', nombre: 'En espera' },
  { valor: 'resuelto', nombre: 'Resuelto' },
  { valor: 'cerrado', nombre: 'Cerrado' },
] as const

const PRIORIDADES = [
  { valor: 'baja', nombre: 'Baja' },
  { valor: 'media', nombre: 'Media' },
  { valor: 'alta', nombre: 'Alta' },
] as const

const ESTILOS_ESTADO: Record<EstadoSolicitud, string> = {
  registrado: 'bg-panel text-texto-secundario',
  en_evaluacion: 'bg-blue-100 text-blue-800',
  asignado: 'bg-indigo-100 text-indigo-800',
  en_atencion: 'bg-amber-100 text-amber-800',
  en_espera: 'bg-orange-100 text-orange-800',
  resuelto: 'bg-emerald-100 text-emerald-800',
  cerrado: 'bg-slate-200 text-slate-700',
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

function TarjetaSolicitud({
  solicitud,
}: {
  solicitud: SolicitudResumen
}) {
  return (
    <article className="rounded-xl border border-panel bg-tarjeta p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide text-texto-secundario">
            {solicitud.numero}
          </p>

          <h3 className="mt-1 break-words text-base font-semibold text-texto">
            {solicitud.titulo}
          </h3>
        </div>

        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold ${
            ESTILOS_ESTADO[solicitud.estado]
          }`}
        >
          {NOMBRES_ESTADO[solicitud.estado]}
        </span>
      </div>

      <div className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-3">
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
          <p className="text-xs text-texto-secundario">Tipo</p>
          <p className="mt-1 font-medium capitalize text-texto">
            {solicitud.tipo}
          </p>
        </div>

        <div>
          <p className="text-xs text-texto-secundario">Prioridad</p>
          <p className="mt-1 font-medium capitalize text-texto">
            {solicitud.prioridad ?? 'No definida'}
          </p>
        </div>

        <div>
          <p className="text-xs text-texto-secundario">
            Fecha de creación
          </p>
          <p className="mt-1 font-medium text-texto">
            {formatearFecha(solicitud.fecha_creacion)}
          </p>
        </div>

        <div>
          <p className="text-xs text-texto-secundario">
            Técnico asignado
          </p>
          <p className="mt-1 font-medium text-texto">
            {solicitud.tecnico_asignado?.nombre ?? 'Sin asignar'}
          </p>
        </div>
      </div>
    </article>
  )
}

export function SolicitudesAsignadasPage() {
  const [resultado, setResultado] = useState<SolicitudesPagina | null>(null)
  const [busqueda, setBusqueda] = useState('')
  const [estado, setEstado] = useState('')
  const [prioridad, setPrioridad] = useState('')
  const [tipo, setTipo] = useState('')
  const [pagina, setPagina] = useState(1)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [recarga, setRecarga] = useState(0)

  useEffect(() => {
    let vigente = true

    const filtros: FiltrosSolicitudes = {
      page: pagina,
      limit: 20,
    }

    if (busqueda.trim()) {
      filtros.busqueda = busqueda.trim()
    }

    if (estado) {
      filtros.estado = estado as EstadoSolicitud
    }

    if (prioridad) {
      filtros.prioridad = prioridad as PrioridadSolicitud
    }

    if (tipo) {
      filtros.tipo = tipo as 'incidente' | 'requerimiento'
    }

    consultarSolicitudesAsignadas(filtros)
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
            : 'No fue posible consultar las solicitudes.',
        )
        setResultado(null)
      })
      .finally(() => {
        if (vigente) {
          setCargando(false)
        }
      })

    return () => {
      vigente = false
    }
  }, [busqueda, estado, prioridad, tipo, pagina, recarga])

  function limpiarFiltros() {
    setBusqueda('')
    setEstado('')
    setPrioridad('')
    setTipo('')
    setPagina(1)
  }

  const totalPaginas = resultado?.pagination.total_pages ?? 0
  const totalSolicitudes = resultado?.pagination.total ?? 0

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-texto">
          Solicitudes asignadas
        </h1>
        <p className="mt-1 text-sm text-texto-secundario">
          Consulta y filtra las solicitudes que tienes asignadas.
        </p>
      </div>

      <div className="rounded-xl border border-panel bg-tarjeta p-5 shadow-sm">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <label
              htmlFor="busqueda"
              className="mb-1 block text-sm font-medium text-texto"
            >
              Buscar
            </label>

            <input
              id="busqueda"
              type="search"
              value={busqueda}
              onChange={(event) => {
                setBusqueda(event.target.value)
                setPagina(1)
              }}
              placeholder="Número o título..."
              className="w-full rounded-lg border border-panel bg-fondo px-3 py-2 text-sm text-texto outline-none transition focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
            />
          </div>

          <div>
            <label
              htmlFor="estado"
              className="mb-1 block text-sm font-medium text-texto"
            >
              Estado
            </label>

            <select
              id="estado"
              value={estado}
              onChange={(event) => {
                setEstado(event.target.value)
                setPagina(1)
              }}
              className="w-full rounded-lg border border-panel bg-fondo px-3 py-2 text-sm text-texto outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
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
            <label
              htmlFor="prioridad"
              className="mb-1 block text-sm font-medium text-texto"
            >
              Prioridad
            </label>

            <select
              id="prioridad"
              value={prioridad}
              onChange={(event) => {
                setPrioridad(event.target.value)
                setPagina(1)
              }}
              className="w-full rounded-lg border border-panel bg-fondo px-3 py-2 text-sm text-texto outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
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
            <label
              htmlFor="tipo"
              className="mb-1 block text-sm font-medium text-texto"
            >
              Tipo de solicitud
            </label>

            <select
              id="tipo"
              value={tipo}
              onChange={(event) => {
                setTipo(event.target.value)
                setPagina(1)
              }}
              className="w-full rounded-lg border border-panel bg-fondo px-3 py-2 text-sm text-texto outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
            >
              <option value="">Todos los tipos</option>
              <option value="incidente">Incidente</option>
              <option value="requerimiento">Requerimiento</option>
            </select>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap justify-end gap-2">
          <Boton
            variante="secundario"
            onClick={limpiarFiltros}
          >
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

      {error && (
        <MensajeEstado
          tipo="error"
          mensaje={error}
        />
      )}

      {cargando ? (
        <Cargando mensaje="Consultando solicitudes asignadas..." />
      ) : (
        <>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm text-texto-secundario">
              {totalSolicitudes}{' '}
              {totalSolicitudes === 1
                ? 'solicitud encontrada'
                : 'solicitudes encontradas'}
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
                <TarjetaSolicitud
                  key={solicitud.id}
                  solicitud={solicitud}
                />
              ))}
            </div>
          ) : (
            !error && (
              <div className="rounded-xl border border-panel bg-tarjeta px-6 py-12 text-center">
                <h2 className="text-lg font-semibold text-texto">
                  No hay solicitudes asignadas
                </h2>
                <p className="mt-2 text-sm text-texto-secundario">
                  No se encontraron solicitudes con los filtros seleccionados.
                </p>
              </div>
            )
          )}

          {totalPaginas > 1 && (
            <div className="flex items-center justify-center gap-3">
              <Boton
                variante="secundario"
                disabled={pagina <= 1}
                onClick={() => setPagina((actual) => actual - 1)}
              >
                Anterior
              </Boton>

              <span className="text-sm text-texto-secundario">
                {pagina} / {totalPaginas}
              </span>

              <Boton
                variante="secundario"
                disabled={pagina >= totalPaginas}
                onClick={() => setPagina((actual) => actual + 1)}
              >
                Siguiente
              </Boton>
            </div>
          )}
        </>
      )}
    </section>
  )
}
