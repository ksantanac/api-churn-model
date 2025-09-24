-- Tabela para armazenar informações dos clientes
CREATE TABLE clientes (
    customer_id VARCHAR PRIMARY KEY,
    gender VARCHAR(10),
    senior_citizen INT,
    partner BOOLEAN,
    dependents BOOLEAN,
    tenure INT,
    phone_service BOOLEAN,
    multiple_lines VARCHAR(20),
    internet_service VARCHAR(20),
    online_security VARCHAR(20),
    online_backup VARCHAR(20),
    device_protection VARCHAR(20),
    tech_support VARCHAR(20),
    streaming_tv VARCHAR(20),
    streaming_movies VARCHAR(20),
    contract VARCHAR(20),
    paperless_billing BOOLEAN,
    payment_method VARCHAR(50),
    monthly_charges NUMERIC,
    total_charges NUMERIC
);

-- Tabela para armazenar previsões de churn
CREATE TABLE predicoes (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR REFERENCES clientes(customer_id),
    churn_predito BOOLEAN,
    probabilidade NUMERIC,
    data_predicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);