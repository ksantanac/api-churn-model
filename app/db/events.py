from fastapi import FastAPI
from db.database import database

def create_startup_handler(app: FastAPI):
    @app.on_event("startup")
    async def startup():
        await database.connect()
        print("✅ Banco de dados conectado!")

def create_shutdown_handler(app: FastAPI):
    @app.on_event("shutdown")
    async def shutdown():
        await database.disconnect()
        print("✅ Banco de dados desconectado!")
