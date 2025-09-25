from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, APIRouter
from pathlib import Path

from database import database

from controllers import (
    auth_controller, 
    cliente_controller,
    predict_controller
) 

app = FastAPI(
    title="API CHURN MODEL",
    description="API para gerenciar o modelo de churn de clientes.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# # Libera CORS para todas as origens - PROD
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# roteador principal
API_PREFIX = "/api/v1"
main_router = APIRouter(prefix=API_PREFIX)

# # Mescla a especificação YAML com as rotas
# app.openapi_schema = load_openapi()

# Incluir os outros roteadores no roteador principal
main_router.include_router(auth_controller.router, prefix="/auth")
main_router.include_router(cliente_controller.router)
main_router.include_router(predict_controller.router)

# Incluir o roteador principal no app
app.include_router(main_router)

@app.on_event("startup")
async def startup():
    await database.connect()
    print("✅ Banco de dados conectado!")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("✅ Banco de dados desconectado!")