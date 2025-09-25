from enum import Enum

class ColumnMapping(str, Enum):
    GENDER = "gender"
    SENIOR_CITIZEN = "SeniorCitizen"
    PARTNER = "Partner"
    DEPENDENTS = "Dependents"
    TENURE = "tenure"
    PHONE_SERVICE = "PhoneService"
    MULTIPLE_LINES = "MultipleLines"
    INTERNET_SERVICE = "InternetService"
    ONLINE_SECURITY = "OnlineSecurity"
    ONLINE_BACKUP = "OnlineBackup"
    DEVICE_PROTECTION = "DeviceProtection"
    TECH_SUPPORT = "TechSupport"
    STREAMING_TV = "StreamingTV"
    STREAMING_MOVIES = "StreamingMovies"
    CONTRACT = "Contract"
    PAPERLESS_BILLING = "PaperlessBilling"
    PAYMENT_METHOD = "PaymentMethod"
    MONTHLY_CHARGES = "MonthlyCharges"
    TOTAL_CHARGES = "TotalCharges"

# Para usar como dicionário (útil para rename do pandas)
COLUMN_MAPPING_DICT = {e.name.lower(): e.value for e in ColumnMapping}
