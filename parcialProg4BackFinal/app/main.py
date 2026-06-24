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
from app.modules.Pedido.routerWebsocket import router as pedidos_websocket_router
from app.core.upload_router import router as upload_router
from fastapi.responses import RedirectResponse, Response


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        seed_estado_pedido(session)
        seed_roles(session)
        seed_usuarios(session)
        seed_forma_pago(session)
        seed_unidad_medida()
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
app.include_router(pedidos_websocket_router,prefix="/pedidos_websocket",tags=["pedidos_websocket"])
app.include_router(upload_router, prefix="/api/v1")
#python -m fastapi dev app/main.py

# ─── Favicon ──────────────────────────────────────────────────────────────────
# Evita el error 404 en navegadores que piden /favicon.ico automáticamente.
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    # Responde con contenido vacío y content-type image/x-icon
    return Response(content=b"", media_type="image/x-icon")


# ─── Raíz → redirige al KDS ──────────────────────────────────────────────────
# Para que el usuario acceda directamente al Dashboard de Cocina
# abriendo http://localhost:8000 sin recordar la ruta exacta.
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/api/v1/cocina")


# ─── Health check ────────────────────────────────────────────────────────────
# Endpoint de verificación para monitoreo (load balancers, Docker healthcheck).
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "version": "1.0.0"}


# ─── Debug: rooms activas del ConnectionManager ──────────────────────────────
# Muestra qué sockets están en cada room. Útil para verificar que el cajero
# esté en role:pedidos antes de hacer pruebas de WS.
@app.get("/debug/ws-rooms", tags=["debug"])
def ws_rooms():
    from app.core.websocket import manager
    return {
        "total_connections": manager.get_active_connections_count(),
        "rooms": manager.get_rooms_info(),
    }
