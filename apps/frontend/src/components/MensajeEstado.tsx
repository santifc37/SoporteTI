
type TipoMensaje = 'exito' | 'error' | 'advertencia' | 'info'

interface MensajeEstadoProps {
  tipo: TipoMensaje
  mensaje: string
}

const estilos: Record<TipoMensaje, string> = {
  exito: 'border-exito/30 bg-exito/10 text-exito',
  error: 'border-error/30 bg-error/10 text-error',
  advertencia: 'border-advertencia/30 bg-advertencia/10 text-advertencia',
  info: 'border-accion/30 bg-accion/10 text-accion',
}

export function MensajeEstado({
  tipo,
  mensaje,
}: MensajeEstadoProps) {
  return (
    <div
      role={tipo === 'error' ? 'alert' : 'status'}
      className={`rounded-lg border px-4 py-3 text-sm font-medium ${estilos[tipo]}`}
    >
      {mensaje}
    </div>
  )
}
