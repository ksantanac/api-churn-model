from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta

from models.token_models import Token, RefreshTokenRequest
from models.user_schema import User
from services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    create_user,
    refresh_access_token,
    get_current_user,
    delete_user,
    REFRESH_TOKEN_EXPIRE_DAYS,
    ACCESS_TOKEN_EXPIRE_MINUTES
    
)
from database import get_db
from sqlalchemy.orm import Session

# Roteador principal para endpoints de autenticação (tag para documentação Swagger/OpenAPI)
router = APIRouter(tags=["Authentication"])

# Configuração do esquema OAuth2 (URL padrão para obtenção de token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Endpoint para login e geração de tokens (access + refresh)
@router.post("/createToken", response_model=Token)
async def login_for_access_token(
    user_data: User,  # Agora espera JSON  # Formulário padrão de login
    db: Session = Depends(get_db)  # Injeção da sessão do banco
):
    # Autentica o usuário no banco de dados
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        # Falha na autenticação retorna HTTP 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria access token com tempo de expiração (em minutos)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Cria refresh token com tempo de expiração maior (em dias)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    
    # Retorna ambos os tokens no formato padrão OAuth2
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# Endpoint para renovação do access token usando refresh token
@router.post("/refreshToken", response_model=Token)
async def refresh_token_endpoint(
    request: RefreshTokenRequest,  # Recebe o refresh token no corpo da requisição
    db: Session = Depends(get_db)   # Sessão do DB
):
    # Chama o serviço de renovação de token
    return refresh_access_token(request.refresh_token, db)

# Endpoint para criação de novos usuários
@router.post("/createUser", status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user: User,  # Dados do usuário validados pelo schema
    db: Session = Depends(get_db)  # Sessão do DB
):
    # Chama o serviço de criação de usuário
    return create_user(db, user.username, user.password)

# Endpoint para deletar usuários
@router.delete("/user/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user_endpoint(
    user_id: int,  # ID do usuário a ser deletado (via path parameter)
    db: Session = Depends(get_db),  # Sessão do DB
    current_user: str = Depends(get_current_user)  # Valida usuário logado
):
    # Chama o serviço de deleção
    return delete_user(db, user_id)