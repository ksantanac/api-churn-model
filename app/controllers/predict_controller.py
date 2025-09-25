from fastapi import APIRouter, HTTPException, Depends

from services.auth_service import get_current_user
from services.predict_service import predict_client_by_id

router = APIRouter()

@router.get("/predict/{customer_id}", summary="Prever churn para cliente existente")
async def predict_client(customer_id: int, current_user: str = Depends(get_current_user)):
    resultado = await predict_client_by_id(customer_id)
    if "error" in resultado:
        raise HTTPException(status_code=404, detail=resultado["error"])
    return resultado
