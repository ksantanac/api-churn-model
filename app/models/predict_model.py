from pydantic import BaseModel

class PredicaoResponse(BaseModel):
    customer_id: str
    churn_predito: bool
    probabilidade: float
