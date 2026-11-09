"""Control de acceso por rol (RF-02, RNF-05).

Uso en una ruta:

    @router.get("", dependencies=[Depends(requiere_rol("coordinador"))])

o, si la ruta necesita al usuario:

    usuario: UsuarioActual = Depends(requiere_rol("coordinador"))
"""

from collections.abc import Callable

from fastapi import Depends

from app.api.dependencies import UsuarioActual, get_current_user
from app.core.errors import ApiError


def requiere_rol(*roles: str) -> Callable[..., UsuarioActual]:
    """Exige una sesión válida y uno de los roles indicados.

    Sin sesión responde 401 (lo hace get_current_user); con otro rol, 403.
    """

    def dependencia(usuario: UsuarioActual = Depends(get_current_user)) -> UsuarioActual:
        if usuario.rol not in roles:
            raise ApiError(
                403, "PERMISO_DENEGADO", "No tienes permisos para realizar esta operación."
            )
        return usuario

    return dependencia
