"""
Script de seed — carga usuarios iniciales para pruebas.
Idempotente: se puede ejecutar múltiples veces sin duplicar datos.

Uso:
    python -m app.db.seed

Requiere PostgreSQL corriendo con las variables de .env configuradas.

Crea:
  - admin / Admin1234!  (role=admin)
  - juan / Juan1234!    (role=user)
"""

from sqlmodel import Session, select, text
from app.core.security import hash_password
from app.modules.usuarios.model import Usuario


USUARIOS_INICIALES = [
    {
        "nombre": "Admin",
        "apellido": "Sistema",
        "email": "admin@example.com",
        "celular": "0000000000",
        "password": "Admin1234!",
        "rol": "ADMIN",
    },
    {
        "nombre": "Juan",
        "apellido": "Perez",
        "email": "juan@example.com",
        "celular": "1111111111",
        "password": "Juan1234!",
        "rol": "CLIENT",
    },
]

def run(session: Session) -> None:
    print("=== Seed Usuarios ===")

    for data in USUARIOS_INICIALES:
        try:
            existing = session.exec(
                select(Usuario).where(Usuario.email == data["email"])
            ).first()

            if existing:
                print(f" [=] Ya existe: {data['email']}")
                continue

            usuario = Usuario(
                nombre=data["nombre"],
                apellido=data["apellido"],
                email=data["email"],
                celular=data["celular"],
                password_hash=hash_password(data["password"]),
            )

            session.add(usuario)
            session.flush()

            session.execute(
                text("INSERT INTO usuario_rol (usuario_id, rol_codigo) VALUES (:uid, :rol)"),
                {"uid": usuario.id, "rol": data["rol"]},
            )
            session.commit()
            print(f" [+] Creado: {data['email']} (rol={data['rol']})")

        except Exception as e:
            session.rollback()
            print(f" [!] Error con {data['email']}: {e}")

    print("\nSeed completado.")

