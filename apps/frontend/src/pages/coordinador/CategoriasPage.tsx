
import { useEffect, useState, type FormEvent } from 'react'

import { Boton } from '../../components/Boton'
import { Cargando } from '../../components/Cargando'
import { MensajeEstado } from '../../components/MensajeEstado'
import {
  CLASE_CAMPO,
  CLASE_TARJETA,
  mensajeDeError,
} from '../../components/coordinador/etiquetas'
import {
  actualizarCategoria,
  consultarCategorias,
  crearCategoria,
} from '../../services/coordinador'

import type { Categoria } from '../../types/coordinador'

function FormularioCategoria({
  inicial,
  textoBoton,
  procesando,
  onGuardar,
  onCancelar,
}: {
  inicial: { nombre: string; descripcion: string }
  textoBoton: string
  procesando: boolean
  onGuardar: (nombre: string, descripcion: string) => Promise<boolean>
  onCancelar?: () => void
}) {
  const [nombre, setNombre] = useState(inicial.nombre)
  const [descripcion, setDescripcion] = useState(inicial.descripcion)

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const guardado = await onGuardar(nombre.trim(), descripcion.trim())

    if (guardado && !onCancelar) {
      // Formulario de creación: queda listo para la siguiente categoría.
      setNombre('')
      setDescripcion('')
    }
  }

  return (
    <form onSubmit={(evento) => void enviar(evento)} className="grid gap-3 md:grid-cols-[1fr_2fr_auto] md:items-end">
      <div>
        <label className="mb-1 block text-sm font-medium text-texto">
          Nombre
          <input
            required
            maxLength={100}
            value={nombre}
            onChange={(evento) => setNombre(evento.target.value)}
            placeholder="Ej. Redes"
            className={`${CLASE_CAMPO} mt-1 font-normal`}
          />
        </label>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-texto">
          Descripción (opcional)
          <input
            maxLength={500}
            value={descripcion}
            onChange={(evento) => setDescripcion(evento.target.value)}
            placeholder="Qué tipo de casos agrupa"
            className={`${CLASE_CAMPO} mt-1 font-normal`}
          />
        </label>
      </div>

      <div className="mb-1 flex gap-2">
        {onCancelar && (
          <Boton type="button" variante="secundario" onClick={onCancelar}>
            Cancelar
          </Boton>
        )}
        <Boton type="submit" disabled={procesando}>
          {textoBoton}
        </Boton>
      </div>
    </form>
  )
}

export function CategoriasPage() {
  const [categorias, setCategorias] = useState<Categoria[]>([])
  const [filtro, setFiltro] = useState<'todas' | 'activas' | 'inactivas'>('todas')
  const [editando, setEditando] = useState<string | null>(null)
  const [recarga, setRecarga] = useState(0)

  const [cargando, setCargando] = useState(true)
  const [procesando, setProcesando] = useState(false)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')

  useEffect(() => {
    let vigente = true

    consultarCategorias({
      activa: filtro === 'todas' ? undefined : filtro === 'activas',
      limit: 100,
    })
      .then((respuesta) => {
        if (vigente) setCategorias(respuesta.data)
      })
      .catch((err: unknown) => {
        if (vigente) setError(mensajeDeError(err, 'No fue posible consultar las categorías.'))
      })
      .finally(() => {
        if (vigente) setCargando(false)
      })

    return () => {
      vigente = false
    }
  }, [filtro, recarga])

  async function ejecutar(
    accion: () => Promise<unknown>,
    exito: string,
    fallo: string,
  ): Promise<boolean> {
    setProcesando(true)
    setError('')
    setMensaje('')

    try {
      await accion()
      setMensaje(exito)
      setEditando(null)
      setRecarga((valor) => valor + 1)
      return true
    } catch (err) {
      setError(mensajeDeError(err, fallo))
      return false
    } finally {
      setProcesando(false)
    }
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-texto">Categorías</h1>
        <p className="mt-1 text-sm text-texto-secundario">
          Organiza las solicitudes por área. Una categoría inactiva deja de
          ofrecerse a los solicitantes, pero las solicitudes que ya la usan la conservan.
        </p>
      </div>

      {error && <MensajeEstado tipo="error" mensaje={error} />}
      {mensaje && <MensajeEstado tipo="exito" mensaje={mensaje} />}

      <div className={CLASE_TARJETA}>
        <h2 className="mb-4 text-lg font-semibold text-texto">Nueva categoría</h2>
        <FormularioCategoria
          inicial={{ nombre: '', descripcion: '' }}
          textoBoton="Crear"
          procesando={procesando}
          onGuardar={(nombre, descripcion) =>
            ejecutar(
              () => crearCategoria({ nombre, descripcion: descripcion || null }),
              'La categoría se creó correctamente.',
              'No fue posible crear la categoría.',
            )
          }
        />
      </div>

      <div className="flex flex-wrap gap-2">
        {(['todas', 'activas', 'inactivas'] as const).map((opcion) => (
          <button
            key={opcion}
            type="button"
            onClick={() => setFiltro(opcion)}
            className={`rounded-full px-4 py-2 text-sm font-semibold capitalize transition ${
              filtro === opcion
                ? 'bg-primario text-white shadow-sm'
                : 'border border-panel bg-tarjeta text-texto hover:bg-panel'
            }`}
          >
            {opcion}
          </button>
        ))}
      </div>

      {cargando ? (
        <Cargando mensaje="Consultando categorías..." />
      ) : categorias.length > 0 ? (
        <div className="space-y-3">
          {categorias.map((categoria) => (
            <article key={categoria.id} className={CLASE_TARJETA}>
              {editando === categoria.id ? (
                <FormularioCategoria
                  inicial={{
                    nombre: categoria.nombre,
                    descripcion: categoria.descripcion ?? '',
                  }}
                  textoBoton="Guardar"
                  procesando={procesando}
                  onCancelar={() => setEditando(null)}
                  onGuardar={(nombre, descripcion) =>
                    ejecutar(
                      () =>
                        actualizarCategoria(categoria.id, {
                          nombre,
                          descripcion: descripcion || null,
                        }),
                      'La categoría se actualizó correctamente.',
                      'No fue posible actualizar la categoría.',
                    )
                  }
                />
              ) : (
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-texto">{categoria.nombre}</h3>
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                          categoria.activa
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-slate-200 text-slate-700'
                        }`}
                      >
                        {categoria.activa ? 'Activa' : 'Inactiva'}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-texto-secundario">
                      {categoria.descripcion || 'Sin descripción'}
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <Boton variante="secundario" onClick={() => setEditando(categoria.id)}>
                      Editar
                    </Boton>
                    <Boton
                      variante={categoria.activa ? 'peligro' : 'primario'}
                      disabled={procesando}
                      onClick={() =>
                        void ejecutar(
                          () => actualizarCategoria(categoria.id, { activa: !categoria.activa }),
                          categoria.activa
                            ? 'La categoría se desactivó.'
                            : 'La categoría se activó.',
                          'No fue posible cambiar el estado de la categoría.',
                        )
                      }
                    >
                      {categoria.activa ? 'Desactivar' : 'Activar'}
                    </Boton>
                  </div>
                </div>
              )}
            </article>
          ))}
        </div>
      ) : (
        <div className="rounded-xl border border-panel bg-tarjeta px-6 py-12 text-center">
          <p className="text-sm text-texto-secundario">No hay categorías para mostrar.</p>
        </div>
      )}
    </section>
  )
}
