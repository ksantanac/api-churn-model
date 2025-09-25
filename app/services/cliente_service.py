import os

import pandas as pd

from datetime import datetime
from joblib import load

from sqlalchemy import text

from database import database
from models.cliente_model import Cliente

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


async def get_client(customer_id: str):
    query = "SELECT * FROM clientes WHERE customer_id = :customer_id"
    return await database.fetch_one(query, {"customer_id": customer_id})

async def predict_client(cliente: Cliente):
    # Inserir cliente no banco
    customer_id = await add_client(cliente)
    print("Cliente inserido no banco:")

    # Transformar em dataframe/array para modelo
    df = pd.DataFrame([cliente.dict()])

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

    # Fazer predição
    prob = model.predict_proba(df)[0][1]
    churn_predito = bool(prob > 0.5)

    # Salvar resultado na tabela predicoes
    query = """
        INSERT INTO predicoes (customer_id, churn_predito, probabilidade, data_predicao)
        VALUES (:customer_id, :churn_predito, :probabilidade, :data_predicao)
    """
    values = {
        "customer_id": customer_id,
        "churn_predito": churn_predito,
        "probabilidade": float(prob),
        "data_predicao": datetime.now(),
    }
    await database.execute(query, values)

    return values