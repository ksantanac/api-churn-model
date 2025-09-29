from fastapi import APIRouter, HTTPException, Depends

from app.models.predict_model import PredictResponse

from app.services.auth_service import get_current_user
from app.services.predict_service import predict_client_by_id

router = APIRouter()

@router.get("/predict/{customer_id}", summary="Prever churn para cliente existente", response_model=PredictResponse)
async def predict_client(customer_id: int, current_user: str = Depends(get_current_user)):
    resultado = await predict_client_by_id(customer_id)
    if not resultado:
        raise HTTPException(status_code=404, detail=f"Cliente {customer_id} não encontrado")
    return resultado
