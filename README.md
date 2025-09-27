# 🚀 API de Churn Prediction

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/) 
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/) 
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg)](https://www.mysql.com/) 
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

API desenvolvida em **FastAPI** para gerenciamento de clientes e previsão de **churn (cancelamento)** com base em um modelo de Machine Learning.

---

## ✨ Funcionalidades

- 🔐 **Autenticação JWT** (login, refresh, criação e exclusão de usuários)  
- 👥 **Gerenciamento de clientes** (cadastro e consulta por ID)  
- 📊 **Previsão de churn**:  
  - Previsão direta a partir de payload (`POST /predict`)  
  - Previsão de clientes já cadastrados (`GET /predict/{id}`)  
- 🗄️ **Banco MySQL** com scripts SQL prontos  
- 📖 **Documentação automática** via Swagger e ReDoc  

---

## 📂 Estrutura do Projeto

```
app/
 ├─ main.py
 ├─ controllers/        # Endpoints
 │   ├─ auth_controller.py
 │   ├─ cliente_controller.py
 │   └─ predict_controller.py
 ├─ services/           # Regras de negócio
 │   ├─ auth_service.py
 │   ├─ cliente_service.py
 │   ├─ predict_service.py
 │   └─ package/pipeline_churn.joblib
 ├─ models/             # Modelos Pydantic
 ├─ db/                 # Banco de dados (MySQL)
 │   └─ sql/tables.sql
 └─ config/column_mapping.py
```

---

## ⚙️ Requisitos

- Python **3.11+**
- MySQL configurado
- Dependências:
```bash
pip install -r requirements.txt
```

---

## 🔑 Variáveis de Ambiente (`.env`)

```env
DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/churn_db

SECRET_KEY=uma_chave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## ▶️ Como Rodar

```bash
uvicorn app.main:app --reload
```

Acesse:
- Swagger UI 👉 [http://localhost:8000/docs](http://localhost:8000/docs)  
- ReDoc 👉 [http://localhost:8000/redoc](http://localhost:8000/redoc)  

---

## 🔒 Autenticação

Fluxo de login via **JWT Bearer Token**:

### ➕ Criar Usuário
```http
POST /auth/createUser
```
```json
{
  "username": "admin",
  "password": "123456"
}
```

### 🔑 Gerar Token
```http
POST /auth/createToken
```
```json
{
  "username": "admin",
  "password": "123456"
}
```

Resposta:
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### ♻️ Refresh Token
```http
POST /auth/refreshToken
```

### ❌ Deletar Usuário
```http
DELETE /auth/user/{user_id}
```

---

## 👥 Clientes

### ➕ Criar Cliente
```http
POST /clientes
Authorization: Bearer <token>
```

Exemplo:
```json
{
  "gender": "Female",
  "senior_citizen": 0,
  "partner": 1,
  "dependents": 0,
  "tenure": 34,
  "phone_service": 1,
  "multiple_lines": "Yes",
  "internet_service": "DSL",
  "online_security": "No",
  "online_backup": "Yes",
  "device_protection": "No",
  "tech_support": "No",
  "streaming_tv": "Yes",
  "streaming_movies": "No",
  "contract": "Month-to-month",
  "paperless_billing": 1,
  "payment_method": "Electronic check",
  "monthly_charges": 75.32,
  "total_charges": 2560.88
}
```

### 🔍 Buscar Cliente
```http
GET /clientes/{customer_id}
Authorization: Bearer <token>
```

---

## 📊 Previsões de Churn

### 🔮 Criar Cliente + Prever
```http
POST /predict
Authorization: Bearer <token>
```

Resposta:
```json
{
  "msg": "Cliente inserido e predição realizada com sucesso!",
  "resultado": {
    "customer_id": 123,
    "churn_predito": true,
    "probabilidade": 0.87
  }
}
```

### 📈 Prever Cliente Existente
```http
GET /predict/{customer_id}
Authorization: Bearer <token>
```

Resposta:
```json
{
  "customer_id": 123,
  "churn_predito": false,
  "probabilidade": 0.23
}
```

---

## 🗄️ Banco de Dados

Script em `app/db/sql/tables.sql`:
```sql
CREATE TABLE clientes (...);
CREATE TABLE predicoes (...);
CREATE TABLE usuarios (...);
```

---

## 📜 Licença

Este projeto é apenas para fins educacionais e segue a licença **MIT**.

