
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

import { Boton } from '../Boton'
import { MensajeEstado } from '../MensajeEstado'
import { api } from '../../services/api'

import type { TipoSolicitud } from '../../types/solicitud'

interface Categoria {
  id: string
  nombre: string
}

interface CategoriasPagina {
  data: Categoria[]
}

interface FormularioSolicitud {
  titulo: string
  descripcion: string
  tipo: TipoSolicitud
  categoria_id: string
  ubicacion: string
  placa_equipo: string
  medio_contacto: 'correo' | 'telefono'
  dato_contacto: string
}

interface FormularioNuevaSolicitudProps {
  onCerrar: () => void
  onCreada: () => void
}

const FORMULARIO_INICIAL: FormularioSolicitud = {
  titulo: '',
  descripcion: '',
  tipo: 'incidente',
  categoria_id: '',
  ubicacion: '',
  placa_equipo: '',
  medio_contacto: 'correo',
  dato_contacto: '',
}

const CAMPO =
  'mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 hover:border-slate-400 focus:border-blue-600 focus:ring-2 focus:ring-blue-100'

const ETIQUETA = 'block text-sm font-semibold text-slate-700'

export function FormularioNuevaSolicitud({
  onCerrar,
  onCreada,
}: FormularioNuevaSolicitudProps) {
  const [formulario, setFormulario] =
    useState<FormularioSolicitud>(FORMULARIO_INICIAL)
  const [categorias, setCategorias] = useState<Categoria[]>([])
  const [cargandoCategorias, setCargandoCategorias] = useState(true)
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let vigente = true

    api<CategoriasPagina>('/categories?limit=100')
      .then((respuesta) => {
        if (vigente) {
          setCategorias(respuesta.data)
        }
      })
      .catch(() => {
        if (vigente) {
          setError('No fue posible cargar las categorías.')
        }
      })
      .finally(() => {
        if (vigente) {
          setCargandoCategorias(false)
        }
      })

    return () => {
      vigente = false
    }
  }, [])

  function actualizar<K extends keyof FormularioSolicitud>(
    campo: K,
    valor: FormularioSolicitud[K],
  ) {
    setFormulario((actual) => ({
      ...actual,
      [campo]: valor,
    }))
  }

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError('')
    setEnviando(true)

    try {
      await api('/requests', {
        method: 'POST',
        datos: {
          titulo: formulario.titulo.trim(),
          descripcion: formulario.descripcion.trim(),
          tipo: formulario.tipo,
          categoria_id: formulario.categoria_id || null,
          ubicacion: formulario.ubicacion.trim(),
          placa_equipo: formulario.placa_equipo.trim() || null,
          medio_contacto: formulario.medio_contacto,
          dato_contacto: formulario.dato_contacto.trim(),
        },
      })

      onCreada()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'No fue posible registrar la solicitud.',
      )
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-950/60 p-2 sm:p-4">
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-nueva-solicitud"
        className="flex max-h-[96dvh] w-full max-w-2xl flex-col overflow-hidden rounded-xl border border-slate-200 bg-slate-50 shadow-2xl sm:max-h-[92dvh] sm:rounded-2xl"
      >
        <header className="flex shrink-0 items-center justify-between gap-4 border-b border-slate-200 bg-white px-4 py-3 sm:px-7 sm:py-4">
          <div>
            <h2
              id="titulo-nueva-solicitud"
              className="text-lg font-bold text-slate-900 sm:text-xl"
            >
              Nueva solicitud
            </h2>

            <p className="mt-1 text-xs text-slate-500 sm:text-sm">
              Cuéntanos qué problema o requerimiento necesitas reportar.
            </p>
          </div>

          <button
            type="button"
            onClick={onCerrar}
            aria-label="Cerrar formulario"
            className="shrink-0 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-lg text-slate-600 hover:bg-slate-100"
          >
            ×
          </button>
        </header>

        <form
          onSubmit={enviarFormulario}
          className="flex min-h-0 flex-1 flex-col"
        >
          <div className="min-h-0 flex-1 space-y-4 overflow-y-auto overscroll-contain p-4 sm:space-y-5 sm:p-7">
            {error && <MensajeEstado tipo="error" mensaje={error} />}

            <div>
              <label htmlFor="titulo" className={ETIQUETA}>
                Título de la solicitud *
              </label>

              <input
                id="titulo"
                required
                maxLength={200}
                value={formulario.titulo}
                onChange={(e) => actualizar('titulo', e.target.value)}
                placeholder="Ej. No funciona mi computador"
                className={CAMPO}
              />
            </div>

            <div>
              <label htmlFor="descripcion" className={ETIQUETA}>
                Descripción del problema *
              </label>

              <textarea
                id="descripcion"
                required
                maxLength={5000}
                rows={3}
                value={formulario.descripcion}
                onChange={(e) => actualizar('descripcion', e.target.value)}
                placeholder="Describe detalladamente lo que sucede..."
                className={`${CAMPO} resize-y`}
              />
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="tipo" className={ETIQUETA}>
                  Tipo de solicitud *
                </label>

                <select
                  id="tipo"
                  value={formulario.tipo}
                  onChange={(e) =>
                    actualizar('tipo', e.target.value as TipoSolicitud)
                  }
                  className={CAMPO}
                >
                  <option value="incidente">Incidente</option>
                  <option value="requerimiento">Requerimiento</option>
                </select>
              </div>

              <div>
                <label htmlFor="categoria" className={ETIQUETA}>
                  Categoría
                </label>

                <select
                  id="categoria"
                  value={formulario.categoria_id}
                  onChange={(e) => actualizar('categoria_id', e.target.value)}
                  disabled={cargandoCategorias}
                  className={CAMPO}
                >
                  <option value="">
                    {cargandoCategorias
                      ? 'Cargando categorías...'
                      : 'Seleccionar categoría'}
                  </option>

                  {categorias.map((categoria) => (
                    <option key={categoria.id} value={categoria.id}>
                      {categoria.nombre}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="ubicacion" className={ETIQUETA}>
                  Ubicación *
                </label>

                <input
                  id="ubicacion"
                  required
                  maxLength={200}
                  value={formulario.ubicacion}
                  onChange={(e) => actualizar('ubicacion', e.target.value)}
                  placeholder="Ej. Bloque A, oficina 203"
                  className={CAMPO}
                />
              </div>

              <div>
                <label htmlFor="placa_equipo" className={ETIQUETA}>
                  Placa del equipo
                </label>

                <input
                  id="placa_equipo"
                  maxLength={50}
                  value={formulario.placa_equipo}
                  onChange={(e) =>
                    actualizar('placa_equipo', e.target.value)
                  }
                  placeholder="Si aplica"
                  className={CAMPO}
                />
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <h3 className="text-sm font-semibold text-slate-800">
                Datos de contacto
              </h3>

              <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label htmlFor="medio_contacto" className={ETIQUETA}>
                    Medio de contacto *
                  </label>

                  <select
                    id="medio_contacto"
                    value={formulario.medio_contacto}
                    onChange={(e) =>
                      actualizar(
                        'medio_contacto',
                        e.target.value as 'correo' | 'telefono',
                      )
                    }
                    className={CAMPO}
                  >
                    <option value="correo">Correo electrónico</option>
                    <option value="telefono">Teléfono</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="dato_contacto" className={ETIQUETA}>
                    {formulario.medio_contacto === 'correo'
                      ? 'Correo electrónico *'
                      : 'Número de teléfono *'}
                  </label>

                  <input
                    id="dato_contacto"
                    required
                    maxLength={255}
                    type={
                      formulario.medio_contacto === 'correo' ? 'email' : 'tel'
                    }
                    value={formulario.dato_contacto}
                    onChange={(e) =>
                      actualizar('dato_contacto', e.target.value)
                    }
                    placeholder={
                      formulario.medio_contacto === 'correo'
                        ? 'nombre@correo.com'
                        : '300 123 4567'
                    }
                    className={CAMPO}
                  />
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-500">
              Los campos marcados con * son obligatorios. La prioridad será
              establecida durante la evaluación de la solicitud.
            </p>
          </div>

          <footer className="flex shrink-0 flex-col-reverse gap-2 border-t border-slate-200 bg-white p-3 sm:flex-row sm:justify-end sm:px-7 sm:py-4">
            <Boton
              variante="secundario"
              onClick={onCerrar}
              disabled={enviando}
            >
              Cancelar
            </Boton>

            <button
              type="submit"
              disabled={enviando}
              className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {enviando ? 'Registrando...' : 'Enviar solicitud'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}
