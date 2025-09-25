import joblib
import pandas as pd

from sqlalchemy import text

from app.database import engine
from app.models.cliente_model import Cliente

# carregar modelo .pkl
pipeline = joblib.load("pipeline_churn.pkl")

def predizer(cliente: Cliente):
    # Converter JSON em DataFrame
    df = pd.DataFrame([cliente.dict()])
    df_features = df.drop(columns=["customer_id"])

    # Predição
    prob = pipeline.predict_proba(df_features)[:, 1][0]
    pred = bool(pipeline.predict(df_features)[0])

    # Salvar predição
    insert_pred = text("""
        INSERT INTO predicoes (customer_id, churn_predito, probabilidade)
        VALUES (:customer_id, :pred, :prob)
    """)
    with engine.connect() as conn:
        conn.execute(insert_pred, {
            "customer_id": cliente.customer_id,
            "pred": pred,
            "prob": prob
        })
        conn.commit()

    return {"customer_id": cliente.customer_id, "churn_predito": pred, "probabilidade": prob}
