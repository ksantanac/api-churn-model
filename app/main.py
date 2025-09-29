import yaml

from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, APIRouter
from pathlib import Path

from app.db.events import create_startup_handler, create_shutdown_handler

from app.controllers import (
    auth_controller, 
    cliente_controller,
    predict_controller
) 

def load_openapi():
    BASE_DIR = Path(__file__).resolve().parent.parent
    with open(BASE_DIR / "openapi.yaml", encoding='utf-8') as f:
        return yaml.safe_load(f)

app = FastAPI(
    title="API CHURN MODEL",
    description="API para gerenciar o modelo de churn de clientes.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Libera CORS para todas as origens - PROD
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Eventos de ciclo de vida
create_startup_handler(app)
create_shutdown_handler(app)

# roteador principal
API_PREFIX = "/api/v1"
main_router = APIRouter(prefix=API_PREFIX)

# # Mescla a especificação YAML com as rotas
app.openapi_schema = load_openapi()

# Incluir os outros roteadores no roteador principal
main_router.include_router(auth_controller.router, prefix="/auth")
main_router.include_router(cliente_controller.router)
main_router.include_router(predict_controller.router)

# Incluir o roteador principal no app
app.include_router(main_router)