from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_db_and_tables
from app.modules.Ingrediente.router import router as ingredientes_router
from app.modules.Producto.router import router as productos_router
from app.modules.Categoria.router import router as categorias_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingredientes_router, prefix="/ingredientes")
app.include_router(productos_router, prefix="/productos", tags=["productos"])
app.include_router(categorias_router, prefix="/categorias", tags=["categorias"])

#python -m fastapi dev app/main.py