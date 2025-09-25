import os

import pandas as pd

from datetime import datetime
from joblib import load
from sqlalchemy import text
from database import database
from database import engine
from models.cliente_model import Cliente
from .cliente_service import get_client_by_id

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "package", "pipeline_churn.joblib")

# carregar modelo .pkl
model = load(MODEL_PATH)

async def predict_client_by_id(customer_id: int):
    # Pegar cliente do banco
    cliente_data = await get_client_by_id(customer_id)
    if not cliente_data:
        return {"error": "Cliente não encontrado", "customer_id": customer_id}

    # Converter para DataFrame
    df = pd.DataFrame([dict(cliente_data)])

    # Renomear colunas para bater com o modelo treinado
    df.rename(columns={
        "gender": "gender",
        "senior_citizen": "SeniorCitizen",
        "partner": "Partner",
        "dependents": "Dependents",
        "tenure": "tenure",
        "phone_service": "PhoneService",
        "multiple_lines": "MultipleLines",
        "internet_service": "InternetService",
        "online_security": "OnlineSecurity",
        "online_backup": "OnlineBackup",
        "device_protection": "DeviceProtection",
        "tech_support": "TechSupport",
        "streaming_tv": "StreamingTV",
        "streaming_movies": "StreamingMovies",
        "contract": "Contract",
        "paperless_billing": "PaperlessBilling",
        "payment_method": "PaymentMethod",
        "monthly_charges": "MonthlyCharges",
        "total_charges": "TotalCharges"
    }, inplace=True)

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

    return values