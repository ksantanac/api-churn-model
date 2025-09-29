import os

import pandas as pd

from datetime import datetime
from joblib import load

from sqlalchemy import text

from app.config.column_mapping import COLUMN_MAPPING_DICT
from app.db.database import database
from app.models.cliente_model import Cliente
from app.models.predict_model import PredictResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "package", "pipeline_churn.joblib")

# Carregar modelo já treinado
model = load(MODEL_PATH)

async def add_client(cliente: Cliente):
    query = """
        INSERT INTO clientes (
            gender, senior_citizen, partner, dependents,
            tenure, phone_service, multiple_lines, internet_service,
            online_security, online_backup, device_protection, tech_support,
            streaming_tv, streaming_movies, contract, paperless_billing,
            payment_method, monthly_charges, total_charges
        )
        VALUES (
            :gender, :senior_citizen, :partner, :dependents,
            :tenure, :phone_service, :multiple_lines, :internet_service,
            :online_security, :online_backup, :device_protection, :tech_support,
            :streaming_tv, :streaming_movies, :contract, :paperless_billing,
            :payment_method, :monthly_charges, :total_charges
        )
        RETURNING customer_id
    """
    values = cliente.dict(exclude={"customer_id"})
    customer_id = await database.execute(query, values)

    return customer_id


async def get_client_by_id(customer_id: int):
    query = "SELECT * FROM clientes WHERE customer_id = :customer_id"
    cliente = await database.fetch_one(query, {"customer_id": customer_id})

    if not cliente:
        return None
    
    return cliente

async def add_predict_client(cliente: Cliente) -> PredictResponse:

    # Inserir cliente no banco
    customer_id = await add_client(cliente)
    print(f"Cliente inserido no banco com ID: {customer_id}")

    # Converter para DataFrame
    df = pd.DataFrame([cliente.dict()])
    df.rename(columns=COLUMN_MAPPING_DICT, inplace=True)

    # Predição
    prob = float(model.predict_proba(df)[0][1])
    churn_predito = bool(prob > 0.5)

    # Salvar predição no banco
    query = """
        INSERT INTO predicoes (customer_id, churn_predito, probabilidade, data_predicao)
        VALUES (:customer_id, :churn_predito, :probabilidade, :data_predicao)
    """
    values = {
        "customer_id": customer_id,
        "churn_predito": churn_predito,
        "probabilidade": round(prob, 2),
        "data_predicao": datetime.now(),
    }
    await database.execute(query, values)

    # Retornar via Pydantic
    return PredictResponse(
        customer_id=str(customer_id),
        churn_predito=churn_predito,
        probabilidade=round(prob, 2)
    )