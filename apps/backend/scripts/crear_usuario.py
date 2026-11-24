"""Crea un usuario directamente en la base de datos.

No hay registro público (RN-02) y todavía no existe la gestión de usuarios del
coordinador (RF-03), así que este script sirve para crear la primera cuenta de
coordinador y las cuentas de prueba.

Uso, desde apps/backend y con el entorno virtual activado:

    python -m scripts.crear_usuario Ana Perez ana@organizacion.com coordinador

La contraseña se pide por teclado (no queda en el historial de la terminal).
Roles: solicitante, tecnico, coordinador.
"""

import argparse
import getpass
import sys

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database.session import get_engine
from app.models import Usuario

ROLES = ("solicitante", "tecnico", "coordinador")
LONGITUD_MINIMA = 8


def main() -> int:
    parser = argparse.ArgumentParser(description="Crear un usuario de SoporteTI.")
    parser.add_argument("nombre")
    parser.add_argument("apellido")
    parser.add_argument("correo")
    parser.add_argument("rol", choices=ROLES)
    args = parser.parse_args()

    contrasena = getpass.getpass("Contraseña: ")
    if len(contrasena) < LONGITUD_MINIMA:
        print(f"La contraseña debe tener al menos {LONGITUD_MINIMA} caracteres.")
        return 1
    if contrasena != getpass.getpass("Repite la contraseña: "):
        print("Las contraseñas no coinciden.")
        return 1

    with Session(get_engine()) as db:
        existe = db.scalar(
            select(Usuario.id).where(func.lower(Usuario.correo) == args.correo.strip().lower())
        )
        if existe:
            print("Ya existe un usuario con ese correo.")
            return 1

        db.add(
            Usuario(
                nombre=args.nombre,
                apellido=args.apellido,
                correo=args.correo.strip(),
                password_hash=hash_password(contrasena),
                rol=args.rol,
            )
        )
        db.commit()

    print(f"Usuario {args.correo} creado con el rol {args.rol}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
