from fastapi import APIRouter, HTTPException, Depends

from services.auth_service import get_current_user

from models.cliente_model import Cliente
from services.cliente_service import (
    add_client,
    get_client,
    predict_client
)

router = APIRouter()

# Criar cliente
@router.post("/clientes")
async def add_cliente(cliente: Cliente, current_user: str = Depends(get_current_user)):
    await add_client(cliente)
    return {"msg": "Cliente inserido com sucesso!"}

# Buscar cliente por ID
@router.get("/clientes/{customer_id}", summary="Buscar cliente por ID")
async def get_cliente(customer_id: str, current_user: str = Depends(get_current_user)):
    cliente = await get_client(customer_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

# Criar cliente + rodar predição imediata
@router.post("/predict", summary="Adicionar cliente e prever churn")
async def add_and_predict(cliente: Cliente, current_user: str = Depends(get_current_user)):
    resultado = await predict_client(cliente)
    return {
        "msg": "Cliente inserido e predição realizada com sucesso!",
        "resultado": resultado,
    }
