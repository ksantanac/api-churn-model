from fastapi import APIRouter, HTTPException, Depends

from app.services.auth_service import get_current_user

from app.models.cliente_model import Cliente
from app.services.cliente_service import (
    add_client,
    get_client_by_id,
    add_predict_client
)

router = APIRouter()

# Criar cliente
@router.post("/clientes")
async def add_cliente(cliente: Cliente, current_user: str = Depends(get_current_user)):
    await add_client(cliente)
    return {"msg": "Cliente inserido com sucesso!"}

# Buscar cliente por ID
@router.get("/clientes/{customer_id}", summary="Buscar cliente por ID")
async def get_cliente(customer_id: int, current_user: str = Depends(get_current_user)):
    cliente = await get_client_by_id(customer_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

# Criar cliente + rodar predição imediata
@router.post("/predict", summary="Adicionar cliente e prever churn")
async def add_and_predict_client(cliente: Cliente, current_user: str = Depends(get_current_user)):
    resultado = await add_predict_client(cliente)
    return { "msg": "Cliente inserido e predição realizada com sucesso!", "resultado": resultado}
