from fastapi import APIRouter, HTTPException

from models.cliente_model import Cliente
from services.cliente_service import (
    inserir_cliente,
    buscar_cliente,
    prever_cliente
)

router = APIRouter()

# Criar cliente
@router.post("/clientes")
async def add_cliente(cliente: Cliente):
    await inserir_cliente(cliente)
    return {"msg": "Cliente inserido com sucesso!"}

# Buscar cliente por ID
@router.get("/clientes/{customer_id}", summary="Buscar cliente por ID")
async def get_cliente(customer_id: str):
    cliente = await buscar_cliente(customer_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

# Criar cliente + rodar predição imediata
@router.post("/predict", summary="Adicionar cliente e prever churn")
async def add_and_predict(cliente: Cliente):
    resultado = await prever_cliente(cliente)
    return {
        "msg": "Cliente inserido e predição realizada com sucesso!",
        "resultado": resultado,
    }
