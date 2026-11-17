
import type { CambioHistorial } from '../../types/coordinador'
import {
  CLASE_TARJETA,
  NOMBRES_ROL,
  NOMBRES_TIPO_CAMBIO,
  formatearFecha,
  textoValor,
} from './etiquetas'

function Detalle({ cambio }: { cambio: CambioHistorial }) {
  if (cambio.tipo_cambio === 'creacion') {
    return null
  }

  if (cambio.valor_anterior === null && cambio.valor_nuevo === null) {
    return null
  }

  return (
    <p className="mt-1 text-sm text-texto">
      <span className="text-texto-secundario">
        {textoValor(cambio.valor_anterior)}
      </span>
      <span className="mx-2 text-texto-secundario" aria-hidden="true">→</span>
      <span className="font-semibold">{textoValor(cambio.valor_nuevo)}</span>
    </p>
  )
}

/** RF-28: línea de tiempo con todos los cambios de la solicitud. */
export function HistorialCambios({ cambios }: { cambios: CambioHistorial[] }) {
  return (
    <div className={CLASE_TARJETA}>
      <h2 className="text-lg font-semibold text-texto">
        Historial de cambios
      </h2>
      <p className="mt-1 text-sm text-texto-secundario">
        Cada cambio de estado, clasificación, asignación y cierre, con su responsable.
      </p>

      {cambios.length > 0 ? (
        <ol className="mt-5 space-y-0">
          {cambios.map((cambio, indice) => (
            <li key={cambio.id} className="relative flex gap-4 pb-5 last:pb-0">
              {indice < cambios.length - 1 && (
                <span
                  aria-hidden="true"
                  className="absolute left-[7px] top-5 h-full w-px bg-panel"
                />
              )}

              <span
                aria-hidden="true"
                className="relative mt-1.5 h-[15px] w-[15px] shrink-0 rounded-full border-4 border-blue-100 bg-accion"
              />

              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <p className="text-sm font-semibold text-texto">
                    {NOMBRES_TIPO_CAMBIO[cambio.tipo_cambio] ?? cambio.tipo_cambio}
                  </p>
                  <p className="text-xs text-texto-secundario">
                    {formatearFecha(cambio.fecha_cambio)}
                  </p>
                </div>

                <Detalle cambio={cambio} />

                {cambio.observacion && (
                  <p className="mt-1 whitespace-pre-wrap text-sm italic text-texto-secundario">
                    “{cambio.observacion}”
                  </p>
                )}

                <p className="mt-1 text-xs text-texto-secundario">
                  {cambio.usuario.nombre} · {NOMBRES_ROL[cambio.usuario.rol] ?? cambio.usuario.rol}
                </p>
              </div>
            </li>
          ))}
        </ol>
      ) : (
        <p className="mt-5 rounded-lg bg-fondo p-5 text-center text-sm text-texto-secundario">
          Todavía no hay cambios registrados.
        </p>
      )}
    </div>
  )
}
