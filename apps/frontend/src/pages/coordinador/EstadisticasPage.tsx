
import { useEffect, useState } from 'react'

import { Boton } from '../../components/Boton'
import { Cargando } from '../../components/Cargando'
import { MensajeEstado } from '../../components/MensajeEstado'
import {
  CLASE_CAMPO,
  CLASE_TARJETA,
  ESTADOS,
  PRIORIDADES,
  mensajeDeError,
} from '../../components/coordinador/etiquetas'
import { consultarEstadisticas } from '../../services/coordinador'

import type { Estadisticas } from '../../types/coordinador'

interface Fila {
  clave: string
  nombre: string
  cantidad: number
}

function Indicador({
  titulo,
  valor,
  detalle,
}: {
  titulo: string
  valor: string
  detalle?: string
}) {
  return (
    <div className={CLASE_TARJETA}>
      <p className="text-xs font-semibold uppercase tracking-wide text-texto-secundario">
        {titulo}
      </p>
      <p className="mt-2 text-3xl font-bold tabular-nums text-texto">{valor}</p>
      {detalle && <p className="mt-1 text-xs text-texto-secundario">{detalle}</p>}
    </div>
  )
}

/** Barras horizontales: el número siempre se muestra junto a la barra. */
function Distribucion({
  titulo,
  filas,
  total,
}: {
  titulo: string
  filas: Fila[]
  total: number
}) {
  const maximo = Math.max(1, ...filas.map((fila) => fila.cantidad))

  return (
    <div className={CLASE_TARJETA}>
      <h2 className="text-lg font-semibold text-texto">{titulo}</h2>

      {filas.length > 0 ? (
        <ul className="mt-4 space-y-3">
          {filas.map((fila) => {
            const porcentaje = total > 0 ? Math.round((fila.cantidad / total) * 100) : 0

            return (
              <li key={fila.clave}>
                <div className="flex items-baseline justify-between gap-3 text-sm">
                  <span className="truncate font-medium text-texto">{fila.nombre}</span>
                  <span className="shrink-0 tabular-nums text-texto-secundario">
                    <span className="font-semibold text-texto">{fila.cantidad}</span> · {porcentaje}%
                  </span>
                </div>
                <div className="mt-1.5 h-2 rounded-full bg-panel">
                  <div
                    className="h-2 rounded-full bg-accion"
                    style={{ width: `${(fila.cantidad / maximo) * 100}%` }}
                  />
                </div>
              </li>
            )
          })}
        </ul>
      ) : (
        <p className="mt-4 text-sm text-texto-secundario">Sin datos en el periodo.</p>
      )}
    </div>
  )
}

export function EstadisticasPage() {
  const [datos, setDatos] = useState<Estadisticas | null>(null)
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  const [recarga, setRecarga] = useState(0)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let vigente = true

    consultarEstadisticas(fechaDesde || undefined, fechaHasta || undefined)
      .then((respuesta) => {
        if (!vigente) return
        setDatos(respuesta)
        setError('')
      })
      .catch((err: unknown) => {
        if (vigente) setError(mensajeDeError(err, 'No fue posible consultar las estadísticas.'))
      })
      .finally(() => {
        if (vigente) setCargando(false)
      })

    return () => {
      vigente = false
    }
  }, [fechaDesde, fechaHasta, recarga])

  const total = datos?.total_solicitudes ?? 0

  const porEstado: Fila[] = datos
    ? ESTADOS.map((estado) => ({
        clave: estado.valor,
        nombre: estado.nombre,
        cantidad: datos.por_estado[estado.valor] ?? 0,
      }))
    : []

  const porPrioridad: Fila[] = datos
    ? [
        ...PRIORIDADES.map((prioridad) => ({
          clave: prioridad.valor,
          nombre: prioridad.nombre,
          cantidad: datos.por_prioridad[prioridad.valor] ?? 0,
        })),
        { clave: 'sin', nombre: 'Sin prioridad', cantidad: datos.sin_prioridad },
      ]
    : []

  const porCategoria: Fila[] = datos
    ? [
        ...datos.por_categoria.map((fila) => ({
          clave: fila.categoria_id,
          nombre: fila.nombre,
          cantidad: fila.cantidad,
        })),
        ...(datos.sin_categoria > 0
          ? [{ clave: 'sin', nombre: 'Sin categoría', cantidad: datos.sin_categoria }]
          : []),
      ]
    : []

  const porTecnico: Fila[] = datos
    ? [
        ...datos.por_tecnico.map((fila) => ({
          clave: fila.tecnico_id,
          nombre: fila.nombre,
          cantidad: fila.cantidad,
        })),
        ...(datos.sin_asignar > 0
          ? [{ clave: 'sin', nombre: 'Sin asignar', cantidad: datos.sin_asignar }]
          : []),
      ]
    : []

  const abiertas = datos ? total - (datos.por_estado.cerrado ?? 0) : 0

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-texto">Estadísticas</h1>
        <p className="mt-1 text-sm text-texto-secundario">
          Situación de las solicitudes y sus responsables. El periodo se aplica
          sobre la fecha de creación.
        </p>
      </div>

      <div className={`${CLASE_TARJETA} flex flex-wrap items-end gap-4`}>
        <div>
          <label htmlFor="est-desde" className="mb-1 block text-sm font-medium text-texto">
            Desde
          </label>
          <input
            id="est-desde"
            type="date"
            value={fechaDesde}
            max={fechaHasta || undefined}
            onChange={(evento) => setFechaDesde(evento.target.value)}
            className={CLASE_CAMPO}
          />
        </div>
        <div>
          <label htmlFor="est-hasta" className="mb-1 block text-sm font-medium text-texto">
            Hasta
          </label>
          <input
            id="est-hasta"
            type="date"
            value={fechaHasta}
            min={fechaDesde || undefined}
            onChange={(evento) => setFechaHasta(evento.target.value)}
            className={CLASE_CAMPO}
          />
        </div>
        <div className="flex gap-2">
          <Boton
            variante="secundario"
            onClick={() => {
              setFechaDesde('')
              setFechaHasta('')
            }}
          >
            Todo el tiempo
          </Boton>
          <Boton variante="secundario" onClick={() => setRecarga((valor) => valor + 1)}>
            Actualizar
          </Boton>
        </div>
      </div>

      {error && <MensajeEstado tipo="error" mensaje={error} />}

      {cargando ? (
        <Cargando mensaje="Calculando estadísticas..." />
      ) : (
        datos && (
          <>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <Indicador titulo="Total de solicitudes" valor={String(total)} />
              <Indicador
                titulo="Abiertas"
                valor={String(abiertas)}
                detalle="Todas menos las cerradas"
              />
              <Indicador
                titulo="Sin asignar"
                valor={String(datos.sin_asignar)}
                detalle="Sin técnico responsable"
              />
              <Indicador
                titulo="Tiempo promedio de atención"
                valor={
                  datos.tiempo_promedio_atencion === null
                    ? '—'
                    : `${datos.tiempo_promedio_atencion.toFixed(1)} h`
                }
                detalle={`Del registro a la resolución · ${datos.solicitudes_con_tiempo} resueltas`}
              />
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <Distribucion titulo="Por estado" filas={porEstado} total={total} />
              <Distribucion titulo="Por prioridad" filas={porPrioridad} total={total} />
              <Distribucion titulo="Por categoría" filas={porCategoria} total={total} />
              <Distribucion titulo="Por técnico (asignación actual)" filas={porTecnico} total={total} />
            </div>
          </>
        )
      )}
    </section>
  )
}
