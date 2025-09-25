from pydantic import BaseModel

class PredictResponse(BaseModel):
    customer_id: int
    churn_predito: bool
    probabilidade: float
