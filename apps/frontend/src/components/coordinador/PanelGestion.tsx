
import { useState, type FormEvent } from 'react'

import { Boton } from '../Boton'
import {
  asignarTecnico,
  cerrarSolicitud,
  clasificarSolicitud,
  iniciarEvaluacion,
} from '../../services/coordinador'
import type { SolicitudDetalle } from '../../services/tecnico'
import type { Categoria, UsuarioListado } from '../../types/coordinador'
import type { PrioridadSolicitud } from '../../types/solicitud'
import {
  CLASE_CAMPO,
  CLASE_TARJETA,
  PRIORIDADES,
  mensajeDeError,
} from './etiquetas'

const ESTADOS_REASIGNABLES = ['asignado', 'en_atencion', 'en_espera']

interface PanelGestionProps {
  solicitud: SolicitudDetalle
  categorias: Categoria[]
  tecnicos: UsuarioListado[]
  onExito: (mensaje: string) => Promise<void>
  onError: (mensaje: string) => void
}

/**
 * Acciones del coordinador sobre una solicitud. Cada bloque solo aparece
 * en los estados en que el backend lo permite, para no ofrecer botones
 * que terminarían en un 409.
 */
export function PanelGestion({
  solicitud,
  categorias,
  tecnicos,
  onExito,
  onError,
}: PanelGestionProps) {
  const [procesando, setProcesando] = useState(false)

  const [categoriaId, setCategoriaId] = useState(solicitud.categoria?.id ?? '')
  const [prioridad, setPrioridad] = useState<string>(solicitud.prioridad ?? '')

  const [tecnicoId, setTecnicoId] = useState('')
  const [observacion, setObservacion] = useState('')

  const [motivoCierre, setMotivoCierre] = useState('')

  const cerrada = solicitud.estado === 'cerrado'
  const esPrimeraAsignacion = solicitud.estado === 'en_evaluacion'
  const esReasignacion = ESTADOS_REASIGNABLES.includes(solicitud.estado)

  // Una categoría inactiva no se puede elegir, pero si la solicitud ya la
  // tiene se muestra para no perder el valor actual.
  const opcionesCategoria = categorias.filter(
    (categoria) => categoria.activa || categoria.id === solicitud.categoria?.id,
  )

  // El técnico actual no aparece al reasignar: el backend lo rechazaría.
  const opcionesTecnico = tecnicos.filter(
    (tecnico) => tecnico.id !== solicitud.tecnico_asignado?.id,
  )

  async function ejecutar(accion: () => Promise<unknown>, exito: string, fallo: string) {
    setProcesando(true)

    try {
      await accion()
      await onExito(exito)
      return true
    } catch (err) {
      onError(mensajeDeError(err, fallo))
      return false
    } finally {
      setProcesando(false)
    }
  }

  async function evaluar() {
    await ejecutar(
      () => iniciarEvaluacion(solicitud.id),
      'La solicitud pasó a evaluación.',
      'No fue posible iniciar la evaluación.',
    )
  }

  async function guardarClasificacion(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    const cambios: { categoria_id?: string | null; prioridad?: PrioridadSolicitud } = {}

    if (categoriaId !== (solicitud.categoria?.id ?? '')) {
      cambios.categoria_id = categoriaId || null
    }

    if (prioridad && prioridad !== solicitud.prioridad) {
      cambios.prioridad = prioridad as PrioridadSolicitud
    }

    if (Object.keys(cambios).length === 0) {
      onError('No hay cambios en la clasificación.')
      return
    }

    await ejecutar(
      () => clasificarSolicitud(solicitud.id, cambios),
      'La clasificación se guardó correctamente.',
      'No fue posible guardar la clasificación.',
    )
  }

  async function guardarAsignacion(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    if (!tecnicoId) return

    const listo = await ejecutar(
      () => asignarTecnico(solicitud.id, tecnicoId, observacion),
      esReasignacion
        ? 'La solicitud se reasignó correctamente.'
        : 'El técnico se asignó correctamente.',
      'No fue posible asignar el técnico.',
    )

    if (listo) {
      setTecnicoId('')
      setObservacion('')
    }
  }

  async function cerrar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    const tipo = solicitud.estado === 'resuelto' ? 'solucion' : 'administrativo'

    if (tipo === 'administrativo' && !motivoCierre.trim()) return

    const confirmar = window.confirm(
      tipo === 'solucion'
        ? '¿Confirmas el cierre de esta solicitud? Después no se podrá modificar.'
        : '¿Confirmas el cierre administrativo? La solicitud no se atenderá y no se podrá modificar.',
    )

    if (!confirmar) return

    const listo = await ejecutar(
      () => cerrarSolicitud(solicitud.id, tipo, motivoCierre),
      'La solicitud se cerró correctamente.',
      'No fue posible cerrar la solicitud.',
    )

    if (listo) {
      setMotivoCierre('')
    }
  }

  if (cerrada) {
    return (
      <div className={CLASE_TARJETA}>
        <h2 className="text-lg font-semibold text-texto">
          Gestión de la solicitud
        </h2>
        <p className="mt-4 rounded-lg bg-panel p-3 text-sm text-texto-secundario">
          La solicitud está cerrada. Puedes consultar su información y su
          historial, pero ya no admite cambios.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {solicitud.estado === 'registrado' && (
        <div className={CLASE_TARJETA}>
          <h2 className="text-lg font-semibold text-texto">
            Evaluación
          </h2>
          <p className="mt-1 text-sm text-texto-secundario">
            La solicitud está pendiente de revisión. Inicia la evaluación para
            poder asignarla o cerrarla administrativamente.
          </p>
          <div className="mt-4 flex justify-end">
            <Boton disabled={procesando} onClick={() => void evaluar()}>
              Iniciar evaluación
            </Boton>
          </div>
        </div>
      )}

      <div className={CLASE_TARJETA}>
        <h2 className="text-lg font-semibold text-texto">
          Clasificación
        </h2>
        <p className="mt-1 text-sm text-texto-secundario">
          Define la categoría y la prioridad del caso.
        </p>

        <form onSubmit={guardarClasificacion} className="mt-4 space-y-4">
          <div>
            <label htmlFor="gestion-categoria" className="mb-1 block text-sm font-medium text-texto">
              Categoría
            </label>
            <select
              id="gestion-categoria"
              value={categoriaId}
              onChange={(evento) => setCategoriaId(evento.target.value)}
              className={CLASE_CAMPO}
            >
              <option value="">Sin categoría</option>
              {opcionesCategoria.map((categoria) => (
                <option key={categoria.id} value={categoria.id}>
                  {categoria.nombre}
                  {categoria.activa ? '' : ' (inactiva)'}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="gestion-prioridad" className="mb-1 block text-sm font-medium text-texto">
              Prioridad
            </label>
            <select
              id="gestion-prioridad"
              value={prioridad}
              onChange={(evento) => setPrioridad(evento.target.value)}
              className={CLASE_CAMPO}
            >
              {/* Una vez definida, la prioridad se puede cambiar pero no quitar. */}
              {!solicitud.prioridad && <option value="">Sin definir</option>}
              {PRIORIDADES.map((opcion) => (
                <option key={opcion.valor} value={opcion.valor}>
                  {opcion.nombre}
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-end">
            <Boton type="submit" variante="secundario" disabled={procesando}>
              Guardar clasificación
            </Boton>
          </div>
        </form>
      </div>

      {(esPrimeraAsignacion || esReasignacion) && (
        <div className={CLASE_TARJETA}>
          <h2 className="text-lg font-semibold text-texto">
            {esReasignacion ? 'Reasignar técnico' : 'Asignar técnico'}
          </h2>
          <p className="mt-1 text-sm text-texto-secundario">
            {esReasignacion
              ? `Responsable actual: ${solicitud.tecnico_asignado?.nombre ?? 'sin asignar'}.`
              : 'Elige el técnico que atenderá la solicitud.'}
          </p>

          {esPrimeraAsignacion && !solicitud.prioridad && (
            <p className="mt-3 rounded-lg border border-advertencia/30 bg-advertencia/10 p-3 text-sm font-medium text-advertencia">
              Te recomendamos definir la prioridad antes de asignar.
            </p>
          )}

          <form onSubmit={guardarAsignacion} className="mt-4 space-y-4">
            <div>
              <label htmlFor="gestion-tecnico" className="mb-1 block text-sm font-medium text-texto">
                Técnico
              </label>
              <select
                id="gestion-tecnico"
                required
                value={tecnicoId}
                onChange={(evento) => setTecnicoId(evento.target.value)}
                className={CLASE_CAMPO}
              >
                <option value="">Selecciona un técnico</option>
                {opcionesTecnico.map((tecnico) => (
                  <option key={tecnico.id} value={tecnico.id}>
                    {tecnico.nombre} {tecnico.apellido}
                  </option>
                ))}
              </select>
              {opcionesTecnico.length === 0 && (
                <p className="mt-2 text-xs text-texto-secundario">
                  No hay otros técnicos activos disponibles.
                </p>
              )}
            </div>

            <div>
              <label htmlFor="gestion-observacion" className="mb-1 block text-sm font-medium text-texto">
                Observación (opcional)
              </label>
              <textarea
                id="gestion-observacion"
                rows={2}
                maxLength={500}
                value={observacion}
                onChange={(evento) => setObservacion(evento.target.value)}
                placeholder={
                  esReasignacion
                    ? 'Motivo de la reasignación...'
                    : 'Indicaciones para el técnico...'
                }
                className={CLASE_CAMPO}
              />
            </div>

            <div className="flex justify-end">
              <Boton type="submit" disabled={procesando || !tecnicoId}>
                {esReasignacion ? 'Reasignar' : 'Asignar'}
              </Boton>
            </div>
          </form>
        </div>
      )}

      {(solicitud.estado === 'resuelto' || solicitud.estado === 'en_evaluacion') && (
        <div className={CLASE_TARJETA}>
          <h2 className="text-lg font-semibold text-texto">
            {solicitud.estado === 'resuelto' ? 'Cerrar solicitud' : 'Cierre administrativo'}
          </h2>
          <p className="mt-1 text-sm text-texto-secundario">
            {solicitud.estado === 'resuelto'
              ? 'El técnico registró la solución. Revísala y cierra el caso.'
              : 'Cierra la solicitud sin atenderla, por ejemplo si está duplicada o no corresponde al área.'}
          </p>

          <form onSubmit={cerrar} className="mt-4 space-y-4">
            <textarea
              rows={3}
              maxLength={1000}
              required={solicitud.estado === 'en_evaluacion'}
              value={motivoCierre}
              onChange={(evento) => setMotivoCierre(evento.target.value)}
              placeholder={
                solicitud.estado === 'resuelto'
                  ? 'Comentario de cierre (opcional)...'
                  : 'Motivo del cierre (obligatorio)...'
              }
              className={CLASE_CAMPO}
            />

            <div className="flex justify-end">
              <Boton
                type="submit"
                variante={solicitud.estado === 'resuelto' ? 'primario' : 'peligro'}
                disabled={procesando}
              >
                {solicitud.estado === 'resuelto' ? 'Cerrar por solución' : 'Cerrar administrativamente'}
              </Boton>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}
