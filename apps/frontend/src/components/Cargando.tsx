
interface CargandoProps {
  mensaje?: string
}

export function Cargando({
  mensaje = 'Cargando información...',
}: CargandoProps) {
  return (
    <div
      role="status"
      className="flex min-h-40 flex-col items-center justify-center gap-3 text-texto-secundario"
    >
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-panel border-t-accion" />
      <p className="text-sm font-medium">{mensaje}</p>
    </div>
  )
}
