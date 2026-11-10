
import type { ButtonHTMLAttributes, ReactNode } from 'react'

type VarianteBoton = 'primario' | 'secundario' | 'peligro'

interface BotonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: VarianteBoton
  children: ReactNode
}

const estilos: Record<VarianteBoton, string> = {
  primario: 'bg-primario text-white hover:bg-accion',
  secundario: 'border border-panel bg-tarjeta text-texto hover:bg-panel',
  peligro: 'bg-error text-white hover:bg-red-700',
}

export function Boton({
  variante = 'primario',
  children,
  className = '',
  ...props
}: BotonProps) {
  return (
    <button
      {...props}
      className={`inline-flex items-center justify-center rounded-lg px-4 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 ${estilos[variante]} ${className}`}
    >
      {children}
    </button>
  )
}
