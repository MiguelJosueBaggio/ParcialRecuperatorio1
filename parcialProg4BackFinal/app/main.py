from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from app.core.database import engine
from app.core.database import create_db_and_tables
from app.modules.EstadoPedido.seed import seed_estado_pedido
from app.modules.Ingrediente.router import router as ingredientes_router
from app.modules.Producto.router import router as productos_router
from app.modules.Categoria.router import router as categorias_router
from app.modules.Pedido.router import router as pedidos_router
from app.modules.usuarios.router import router as usuarios_router
from app.modules.Rol.router import router as roles_router   
from app.db.seed import run as seed_usuarios
from app.modules.FormaPago.seed import seed_forma_pago
from app.modules.UnidadMedida.seed import seed_unidad_medida
from app.modules.Rol.seed import seed_roles

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        seed_estado_pedido(session)
        seed_usuarios(session)
        seed_forma_pago(session)
        seed_unidad_medida()
        seed_roles(session)
    yield


app = FastAPI(
    title="Food Store API",
    description="Ejemplo de arquitectura Router → Service → UoW → Repository",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow CORS from frontend dev server. For production, restrict origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000" ,"http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingredientes_router, prefix="/ingredientes")
app.include_router(productos_router, prefix="/productos", tags=["productos"])
app.include_router(categorias_router, prefix="/categorias", tags=["categorias"])
app.include_router(pedidos_router, prefix="/pedidos", tags=["pedidos"]) 
app.include_router(usuarios_router)
app.include_router(roles_router, prefix="/roles", tags=["roles"])

#python -m fastapi dev app/main.py