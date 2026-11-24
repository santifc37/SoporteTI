
import { useEffect, useState, type FormEvent } from 'react'

import { Boton } from '../../components/Boton'
import { Cargando } from '../../components/Cargando'
import { MensajeEstado } from '../../components/MensajeEstado'
import { Paginacion } from '../../components/coordinador/Paginacion'
import {
  CLASE_CAMPO,
  CLASE_TARJETA,
  NOMBRES_ROL,
  formatearFecha,
  mensajeDeError,
} from '../../components/coordinador/etiquetas'
import { useAuth } from '../../hooks/useAuth'
import {
  actualizarUsuario,
  consultarUsuarios,
  crearUsuario,
  restablecerContrasena,
} from '../../services/coordinador'

import type { MedioContacto, RolUsuario } from '../../types/auth'
import type {
  ActualizarUsuarioRequest,
  UsuarioListado,
  UsuariosPagina,
} from '../../types/coordinador'

const ROLES: RolUsuario[] = ['solicitante', 'tecnico', 'coordinador']

interface DatosFormulario {
  nombre: string
  apellido: string
  correo: string
  rol: RolUsuario
  medio_contacto_preferido: MedioContacto
  telefono: string
  contrasena: string
}

const FORMULARIO_VACIO: DatosFormulario = {
  nombre: '',
  apellido: '',
  correo: '',
  rol: 'solicitante',
  medio_contacto_preferido: 'correo',
  telefono: '',
  contrasena: '',
}

function Etiqueta({ htmlFor, children }: { htmlFor: string; children: string }) {
  return (
    <label htmlFor={htmlFor} className="mb-1 block text-sm font-medium text-texto">
      {children}
    </label>
  )
}

/** Formulario compartido para crear y editar. Al editar no se pide contraseña. */
function FormularioUsuario({
  inicial,
  esEdicion,
  esPropio,
  procesando,
  onGuardar,
  onCancelar,
}: {
  inicial: DatosFormulario
  esEdicion: boolean
  esPropio: boolean
  procesando: boolean
  onGuardar: (datos: DatosFormulario) => void
  onCancelar: () => void
}) {
  const [datos, setDatos] = useState(inicial)

  function cambiar<K extends keyof DatosFormulario>(campo: K, valor: DatosFormulario[K]) {
    setDatos((actual) => ({ ...actual, [campo]: valor }))
  }

  function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    onGuardar(datos)
  }

  const prefijo = esEdicion ? 'editar' : 'nuevo'

  return (
    <form onSubmit={enviar} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Etiqueta htmlFor={`${prefijo}-nombre`}>Nombre</Etiqueta>
          <input
            id={`${prefijo}-nombre`}
            required
            maxLength={100}
            value={datos.nombre}
            onChange={(evento) => cambiar('nombre', evento.target.value)}
            className={CLASE_CAMPO}
          />
        </div>

        <div>
          <Etiqueta htmlFor={`${prefijo}-apellido`}>Apellido</Etiqueta>
          <input
            id={`${prefijo}-apellido`}
            required
            maxLength={100}
            value={datos.apellido}
            onChange={(evento) => cambiar('apellido', evento.target.value)}
            className={CLASE_CAMPO}
          />
        </div>

        <div>
          <Etiqueta htmlFor={`${prefijo}-correo`}>Correo electrónico</Etiqueta>
          <input
            id={`${prefijo}-correo`}
            type="email"
            required
            maxLength={255}
            value={datos.correo}
            onChange={(evento) => cambiar('correo', evento.target.value)}
            className={CLASE_CAMPO}
          />
        </div>

        <div>
          <Etiqueta htmlFor={`${prefijo}-rol`}>Rol</Etiqueta>
          <select
            id={`${prefijo}-rol`}
            value={datos.rol}
            disabled={esPropio}
            onChange={(evento) => cambiar('rol', evento.target.value as RolUsuario)}
            className={CLASE_CAMPO}
          >
            {ROLES.map((rol) => (
              <option key={rol} value={rol}>
                {NOMBRES_ROL[rol]}
              </option>
            ))}
          </select>
          {esPropio && (
            <p className="mt-1 text-xs text-texto-secundario">No puedes cambiar tu propio rol.</p>
          )}
        </div>

        <div>
          <Etiqueta htmlFor={`${prefijo}-medio`}>Medio de contacto preferido</Etiqueta>
          <select
            id={`${prefijo}-medio`}
            value={datos.medio_contacto_preferido}
            onChange={(evento) =>
              cambiar('medio_contacto_preferido', evento.target.value as MedioContacto)
            }
            className={CLASE_CAMPO}
          >
            <option value="correo">Correo</option>
            <option value="telefono">Teléfono</option>
          </select>
        </div>

        <div>
          <Etiqueta htmlFor={`${prefijo}-telefono`}>
            {datos.medio_contacto_preferido === 'telefono' ? 'Teléfono' : 'Teléfono (opcional)'}
          </Etiqueta>
          <input
            id={`${prefijo}-telefono`}
            type="tel"
            required={datos.medio_contacto_preferido === 'telefono'}
            minLength={7}
            maxLength={20}
            value={datos.telefono}
            onChange={(evento) => cambiar('telefono', evento.target.value)}
            className={CLASE_CAMPO}
          />
        </div>

        {!esEdicion && (
          <div>
            <Etiqueta htmlFor="nuevo-contrasena">Contraseña inicial</Etiqueta>
            <input
              id="nuevo-contrasena"
              type="password"
              required
              minLength={8}
              maxLength={128}
              autoComplete="new-password"
              value={datos.contrasena}
              onChange={(evento) => cambiar('contrasena', evento.target.value)}
              className={CLASE_CAMPO}
            />
            <p className="mt-1 text-xs text-texto-secundario">Mínimo 8 caracteres.</p>
          </div>
        )}
      </div>

      <div className="flex flex-wrap justify-end gap-2">
        <Boton type="button" variante="secundario" onClick={onCancelar}>
          Cancelar
        </Boton>
        <Boton type="submit" disabled={procesando}>
          {procesando ? 'Guardando...' : esEdicion ? 'Guardar cambios' : 'Crear usuario'}
        </Boton>
      </div>
    </form>
  )
}

function FormularioContrasena({
  usuario,
  procesando,
  onGuardar,
  onCancelar,
}: {
  usuario: UsuarioListado
  procesando: boolean
  onGuardar: (contrasena: string) => void
  onCancelar: () => void
}) {
  const [contrasena, setContrasena] = useState('')
  const [confirmacion, setConfirmacion] = useState('')

  const noCoinciden = confirmacion.length > 0 && contrasena !== confirmacion

  function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (contrasena !== confirmacion) return
    onGuardar(contrasena)
  }

  return (
    <form onSubmit={enviar} className="space-y-4">
      <p className="text-sm text-texto-secundario">
        Asigna una contraseña temporal a {usuario.nombre} {usuario.apellido}. Compártela
        por un medio seguro y pídele que la cambie al ingresar.
      </p>

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Etiqueta htmlFor="temporal">Contraseña temporal</Etiqueta>
          <input
            id="temporal"
            type="password"
            required
            minLength={8}
            maxLength={128}
            autoComplete="new-password"
            value={contrasena}
            onChange={(evento) => setContrasena(evento.target.value)}
            className={CLASE_CAMPO}
          />
        </div>

        <div>
          <Etiqueta htmlFor="temporal-confirmacion">Confirmar contraseña</Etiqueta>
          <input
            id="temporal-confirmacion"
            type="password"
            required
            minLength={8}
            maxLength={128}
            autoComplete="new-password"
            value={confirmacion}
            onChange={(evento) => setConfirmacion(evento.target.value)}
            className={CLASE_CAMPO}
          />
          {noCoinciden && (
            <p className="mt-1 text-xs font-medium text-error">Las contraseñas no coinciden.</p>
          )}
        </div>
      </div>

      <div className="flex flex-wrap justify-end gap-2">
        <Boton type="button" variante="secundario" onClick={onCancelar}>
          Cancelar
        </Boton>
        <Boton type="submit" disabled={procesando || noCoinciden}>
          Restablecer contraseña
        </Boton>
      </div>
    </form>
  )
}

type Panel =
  | { tipo: 'crear' }
  | { tipo: 'editar'; usuario: UsuarioListado }
  | { tipo: 'contrasena'; usuario: UsuarioListado }
  | null

export function UsuariosPage() {
  const { usuario: actual } = useAuth()

  const [resultado, setResultado] = useState<UsuariosPagina | null>(null)
  const [busqueda, setBusqueda] = useState('')
  const [rol, setRol] = useState('')
  const [activo, setActivo] = useState('')
  const [pagina, setPagina] = useState(1)
  const [recarga, setRecarga] = useState(0)

  const [panel, setPanel] = useState<Panel>(null)
  const [cargando, setCargando] = useState(true)
  const [procesando, setProcesando] = useState(false)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')

  useEffect(() => {
    let vigente = true

    consultarUsuarios({
      busqueda,
      rol: (rol || undefined) as RolUsuario | undefined,
      activo: activo === '' ? undefined : activo === 'true',
      page: pagina,
      limit: 20,
    })
      .then((respuesta) => {
        if (vigente) setResultado(respuesta)
      })
      .catch((err: unknown) => {
        if (vigente) setError(mensajeDeError(err, 'No fue posible consultar los usuarios.'))
      })
      .finally(() => {
        if (vigente) setCargando(false)
      })

    return () => {
      vigente = false
    }
  }, [busqueda, rol, activo, pagina, recarga])

  async function ejecutar(accion: () => Promise<unknown>, exito: string, fallo: string) {
    setProcesando(true)
    setError('')
    setMensaje('')

    try {
      await accion()
      setMensaje(exito)
      setPanel(null)
      setRecarga((valor) => valor + 1)
    } catch (err) {
      setError(mensajeDeError(err, fallo))
    } finally {
      setProcesando(false)
    }
  }

  function guardarNuevo(datos: DatosFormulario) {
    void ejecutar(
      () =>
        crearUsuario({
          nombre: datos.nombre.trim(),
          apellido: datos.apellido.trim(),
          correo: datos.correo.trim(),
          contrasena: datos.contrasena,
          rol: datos.rol,
          medio_contacto_preferido: datos.medio_contacto_preferido,
          telefono: datos.telefono.trim() || null,
        }),
      'El usuario se creó correctamente.',
      'No fue posible crear el usuario.',
    )
  }

  function guardarEdicion(usuario: UsuarioListado, datos: DatosFormulario) {
    // Solo se envían los campos que cambiaron (PATCH parcial).
    const cambios: ActualizarUsuarioRequest = {}
    const telefono = datos.telefono.trim() || null

    if (datos.nombre.trim() !== usuario.nombre) cambios.nombre = datos.nombre.trim()
    if (datos.apellido.trim() !== usuario.apellido) cambios.apellido = datos.apellido.trim()
    if (datos.correo.trim() !== usuario.correo) cambios.correo = datos.correo.trim()
    if (datos.rol !== usuario.rol) cambios.rol = datos.rol
    if (datos.medio_contacto_preferido !== usuario.medio_contacto_preferido) {
      cambios.medio_contacto_preferido = datos.medio_contacto_preferido
    }
    if (telefono !== usuario.telefono) cambios.telefono = telefono

    if (Object.keys(cambios).length === 0) {
      setPanel(null)
      return
    }

    void ejecutar(
      () => actualizarUsuario(usuario.id, cambios),
      'El usuario se actualizó correctamente.',
      'No fue posible actualizar el usuario.',
    )
  }

  function cambiarEstado(usuario: UsuarioListado) {
    const desactivar = usuario.activo

    if (
      desactivar &&
      !window.confirm(
        `¿Desactivar la cuenta de ${usuario.nombre} ${usuario.apellido}? No podrá iniciar sesión.`,
      )
    ) {
      return
    }

    void ejecutar(
      () => actualizarUsuario(usuario.id, { activo: !desactivar }),
      desactivar ? 'La cuenta se desactivó.' : 'La cuenta se activó.',
      'No fue posible cambiar el estado de la cuenta.',
    )
  }

  function alCambiar(setter: (valor: string) => void) {
    return (valor: string) => {
      setter(valor)
      setPagina(1)
    }
  }

  const totalPaginas = resultado?.pagination.total_pages ?? 0

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-texto">Usuarios</h1>
          <p className="mt-1 text-sm text-texto-secundario">
            Crea cuentas, asigna roles y administra el acceso al sistema.
          </p>
        </div>

        {panel?.tipo !== 'crear' && (
          <Boton
            onClick={() => {
              setMensaje('')
              setError('')
              setPanel({ tipo: 'crear' })
            }}
          >
            + Nuevo usuario
          </Boton>
        )}
      </div>

      {error && <MensajeEstado tipo="error" mensaje={error} />}
      {mensaje && <MensajeEstado tipo="exito" mensaje={mensaje} />}

      {panel && (
        <div className={`${CLASE_TARJETA} border-blue-200`}>
          <h2 className="mb-4 text-lg font-semibold text-texto">
            {panel.tipo === 'crear' && 'Nuevo usuario'}
            {panel.tipo === 'editar' && `Editar a ${panel.usuario.nombre} ${panel.usuario.apellido}`}
            {panel.tipo === 'contrasena' && 'Restablecer contraseña'}
          </h2>

          {panel.tipo === 'crear' && (
            <FormularioUsuario
              inicial={FORMULARIO_VACIO}
              esEdicion={false}
              esPropio={false}
              procesando={procesando}
              onGuardar={guardarNuevo}
              onCancelar={() => setPanel(null)}
            />
          )}

          {panel.tipo === 'editar' && (
            <FormularioUsuario
              key={panel.usuario.id}
              inicial={{
                nombre: panel.usuario.nombre,
                apellido: panel.usuario.apellido,
                correo: panel.usuario.correo,
                rol: panel.usuario.rol,
                medio_contacto_preferido: panel.usuario.medio_contacto_preferido,
                telefono: panel.usuario.telefono ?? '',
                contrasena: '',
              }}
              esEdicion
              esPropio={panel.usuario.id === actual?.id}
              procesando={procesando}
              onGuardar={(datos) => guardarEdicion(panel.usuario, datos)}
              onCancelar={() => setPanel(null)}
            />
          )}

          {panel.tipo === 'contrasena' && (
            <FormularioContrasena
              key={panel.usuario.id}
              usuario={panel.usuario}
              procesando={procesando}
              onGuardar={(contrasena) =>
                void ejecutar(
                  () => restablecerContrasena(panel.usuario.id, contrasena),
                  'La contraseña se restableció correctamente.',
                  'No fue posible restablecer la contraseña.',
                )
              }
              onCancelar={() => setPanel(null)}
            />
          )}
        </div>
      )}

      <div className={CLASE_TARJETA}>
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <Etiqueta htmlFor="usuarios-busqueda">Buscar</Etiqueta>
            <input
              id="usuarios-busqueda"
              type="search"
              value={busqueda}
              onChange={(evento) => alCambiar(setBusqueda)(evento.target.value)}
              placeholder="Nombre o correo..."
              className={CLASE_CAMPO}
            />
          </div>

          <div>
            <Etiqueta htmlFor="usuarios-rol">Rol</Etiqueta>
            <select
              id="usuarios-rol"
              value={rol}
              onChange={(evento) => alCambiar(setRol)(evento.target.value)}
              className={CLASE_CAMPO}
            >
              <option value="">Todos los roles</option>
              {ROLES.map((opcion) => (
                <option key={opcion} value={opcion}>
                  {NOMBRES_ROL[opcion]}
                </option>
              ))}
            </select>
          </div>

          <div>
            <Etiqueta htmlFor="usuarios-activo">Estado de la cuenta</Etiqueta>
            <select
              id="usuarios-activo"
              value={activo}
              onChange={(evento) => alCambiar(setActivo)(evento.target.value)}
              className={CLASE_CAMPO}
            >
              <option value="">Todas</option>
              <option value="true">Activas</option>
              <option value="false">Inactivas</option>
            </select>
          </div>
        </div>
      </div>

      {cargando ? (
        <Cargando mensaje="Consultando usuarios..." />
      ) : (
        <>
          <p className="text-sm text-texto-secundario">
            {resultado?.pagination.total ?? 0} usuarios encontrados
          </p>

          <div className="overflow-x-auto rounded-xl border border-panel bg-tarjeta shadow-sm">
            <table className="w-full min-w-[760px] text-left text-sm">
              <thead className="border-b border-panel bg-fondo text-xs uppercase tracking-wide text-texto-secundario">
                <tr>
                  <th className="px-4 py-3 font-semibold">Usuario</th>
                  <th className="px-4 py-3 font-semibold">Rol</th>
                  <th className="px-4 py-3 font-semibold">Contacto</th>
                  <th className="px-4 py-3 font-semibold">Estado</th>
                  <th className="px-4 py-3 font-semibold">Creado</th>
                  <th className="px-4 py-3 text-right font-semibold">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-panel">
                {resultado?.data.map((usuario) => {
                  const esPropio = usuario.id === actual?.id

                  return (
                    <tr key={usuario.id} className={usuario.activo ? '' : 'bg-slate-50 text-texto-secundario'}>
                      <td className="px-4 py-3">
                        <p className="font-semibold text-texto">
                          {usuario.nombre} {usuario.apellido}
                          {esPropio && <span className="ml-2 text-xs font-medium text-accion">(tú)</span>}
                        </p>
                        <p className="text-xs text-texto-secundario">{usuario.correo}</p>
                      </td>
                      <td className="px-4 py-3">{NOMBRES_ROL[usuario.rol] ?? usuario.rol}</td>
                      <td className="px-4 py-3 text-xs">
                        {usuario.medio_contacto_preferido === 'telefono'
                          ? `Teléfono: ${usuario.telefono ?? '—'}`
                          : 'Correo'}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                            usuario.activo ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-700'
                          }`}
                        >
                          {usuario.activo ? 'Activa' : 'Inactiva'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs">{formatearFecha(usuario.fecha_creacion)}</td>
                      <td className="px-4 py-3">
                        <div className="flex justify-end gap-1.5">
                          <button
                            type="button"
                            onClick={() => setPanel({ tipo: 'editar', usuario })}
                            className="rounded-lg px-2.5 py-1.5 text-xs font-semibold text-accion hover:bg-blue-50"
                          >
                            Editar
                          </button>
                          <button
                            type="button"
                            onClick={() => setPanel({ tipo: 'contrasena', usuario })}
                            className="rounded-lg px-2.5 py-1.5 text-xs font-semibold text-accion hover:bg-blue-50"
                          >
                            Contraseña
                          </button>
                          {!esPropio && (
                            <button
                              type="button"
                              disabled={procesando}
                              onClick={() => cambiarEstado(usuario)}
                              className={`rounded-lg px-2.5 py-1.5 text-xs font-semibold disabled:opacity-50 ${
                                usuario.activo ? 'text-error hover:bg-red-50' : 'text-exito hover:bg-emerald-50'
                              }`}
                            >
                              {usuario.activo ? 'Desactivar' : 'Activar'}
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>

            {resultado && resultado.data.length === 0 && (
              <p className="p-8 text-center text-sm text-texto-secundario">
                No se encontraron usuarios con los filtros seleccionados.
              </p>
            )}
          </div>

          <Paginacion pagina={pagina} totalPaginas={totalPaginas} onCambiar={setPagina} />
        </>
      )}
    </section>
  )
}
