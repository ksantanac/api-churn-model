from pydantic import BaseModel

# Modelo para representar um token de autenticação
class Token(BaseModel):
    access_token: str  
    refresh_token: str  
    token_type: str  

# Modelo para representar os dados contidos no token
class TokenData(BaseModel):
    username: str | None = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str