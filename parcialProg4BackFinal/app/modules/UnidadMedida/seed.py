from sqlmodel import Session
from app.core.database import engine
from app.modules.UnidadMedida.models import UnidadMedida


UNIDADES_INICIALES = [
    {"nombre": "Kilogramo",      "simbolo": "kg",  "tipo": "masa"},
    {"nombre": "Gramo",          "simbolo": "g",   "tipo": "masa"},
    {"nombre": "Litro",          "simbolo": "L",   "tipo": "volumen"},
    {"nombre": "Mililitro",      "simbolo": "mL",  "tipo": "volumen"},
    {"nombre": "Pieza",          "simbolo": "u",   "tipo": "unidad"},
    {"nombre": "Docena",         "simbolo": "doc", "tipo": "unidad"},
    {"nombre": "Metro cuadrado", "simbolo": "m2",  "tipo": "area"},
]


def seed_unidad_medida() -> None:
    with Session(engine) as session:
        for data in UNIDADES_INICIALES:
            # Buscamos por símbolo (UQ) para verificar si ya existe
            existente = session.exec(
                __import__("sqlmodel").select(UnidadMedida)
                .where(UnidadMedida.simbolo == data["simbolo"])
            ).first()

            if existente:
                print(f"  [=] Ya existe: {data['simbolo']}")
            else:
                session.add(UnidadMedida(**data))
                print(f"  [+] Creado: {data['nombre']} ({data['simbolo']})")

        session.commit()
    print("Seed UnidadMedida ejecutado.")