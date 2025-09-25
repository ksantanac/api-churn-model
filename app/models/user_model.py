from pydantic import BaseModel

# Modelo Pydantic para representar um usuário no sistema
class User(BaseModel):
    username: str 
    password: str  