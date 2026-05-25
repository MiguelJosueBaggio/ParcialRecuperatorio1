from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_db_and_tables
from app.modules.EstadoPedido.seed import seed_estado_pedido
from app.modules.UnidadMedida.seed import seed_unidad_medida

# Dominio 1 — Identidad & Acceso
from app.modules.usuarios.model import Usuario
from app.modules.RefreshToken.models import RefreshToken
from app.modules.Rol.models import Rol, UsuarioRol

# Dominio 2 — Catálogo de Productos
from app.modules.UnidadMedida.models import UnidadMedida
from app.modules.Categoria.models import Categoria
from app.modules.Ingrediente.models import Ingrediente, productoIngredienteLink
from app.modules.Producto.models import Producto

# Dominio 2 — Ventas
from app.modules.EstadoPedido.models import EstadoPedidoModel
from app.modules.Pedido.models import Pedido
from app.modules.DetallePedido.models import DetallePedido

# Routers
from app.modules.usuarios.router import router as auth_router
from app.modules.Ingrediente.router import router as ingredientes_router
from app.modules.Producto.router import router as productos_router
from app.modules.Categoria.router import router as categorias_router
from app.modules.UnidadMedida.router import router as unidades_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_estado_pedido()
    seed_unidad_medida()
    yield


app = FastAPI(
    title="Food Store API",
    description="Arquitectura Router → Service → UoW → Repository",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(ingredientes_router, prefix="/api/v1/ingredientes", tags=["ingredientes"])
app.include_router(productos_router,    prefix="/api/v1/productos",    tags=["productos"])
app.include_router(categorias_router,   prefix="/api/v1/categorias",   tags=["categorias"])
app.include_router(unidades_router,     prefix="/api/v1/unidades-medida", tags=["unidades-medida"])