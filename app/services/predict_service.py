import os

import pandas as pd
from joblib import load
from datetime import datetime

from .cliente_service import get_client_by_id
from config.column_mapping import COLUMN_MAPPING_DICT
from db.database import database
from models.predict_model import PredictResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "package", "pipeline_churn.joblib")

# Carregar modelo uma vez
model = load(MODEL_PATH)

async def predict_client_by_id(customer_id: int) -> PredictResponse:
    """
    Faz a predição de churn para um cliente pelo ID.

    Retorna um modelo PredictResponse com:
    - customer_id
    - churn_predito (bool)
    - probabilidade (float entre 0 e 1)
    """
    # Buscar cliente no banco
    cliente_data = await get_client_by_id(customer_id)
    
    if not cliente_data:
        return None 

    # Converter dados para DataFrame
    df = pd.DataFrame([dict(cliente_data)])
    df.rename(columns=COLUMN_MAPPING_DICT, inplace=True)

    # Predição
    prob = float(model.predict_proba(df)[:, 1][0])
    pred = bool(model.predict(df)[0])

    # Salvar predição no banco
    query_insert = """
        INSERT INTO predicoes (customer_id, churn_predito, probabilidade, data_predicao)
        VALUES (:customer_id, :churn_predito, :probabilidade, :data_predicao)
    """
    values = {
        "customer_id": customer_id,
        "churn_predito": pred,
        "probabilidade": round(prob, 2),
        "data_predicao": datetime.now()
    }
    await database.execute(query_insert, values)

    # Retornar usando Pydantic
    return PredictResponse(
        customer_id=customer_id,
        churn_predito=pred,
        probabilidade=round(prob, 2)
    )
