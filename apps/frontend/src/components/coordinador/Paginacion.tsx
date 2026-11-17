
import { Boton } from '../Boton'

export function Paginacion({
  pagina,
  totalPaginas,
  onCambiar,
}: {
  pagina: number
  totalPaginas: number
  onCambiar: (pagina: number) => void
}) {
  if (totalPaginas <= 1) {
    return null
  }

  return (
    <div className="flex items-center justify-center gap-3">
      <Boton
        variante="secundario"
        disabled={pagina <= 1}
        onClick={() => onCambiar(pagina - 1)}
      >
        Anterior
      </Boton>

      <span className="text-sm text-texto-secundario">
        {pagina} / {totalPaginas}
      </span>

      <Boton
        variante="secundario"
        disabled={pagina >= totalPaginas}
        onClick={() => onCambiar(pagina + 1)}
      >
        Siguiente
      </Boton>
    </div>
  )
}
