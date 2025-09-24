import os

from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db

# Carrega variáveis do .env
load_dotenv()

# Configurações de segurança (agora do .env)
SECRET_KEY = os.getenv("SECRET_KEY") 
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

# Configuração do sistema de hash de senhas (usando bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração do esquema OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Função para verificar se a senha plain-text corresponde ao hash
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Função para gerar hash de senha
def get_password_hash(password: str):
    return pwd_context.hash(password)

# Função para criar novo usuário no banco de dados
def create_user(db: Session, username: str, password: str):
    # Verifica se usuário já existe
    query = text("SELECT username FROM usuarios WHERE username = :username")
    existing_user = db.execute(query, {"username": username}).fetchone()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Cria hash da senha antes de armazenar
    hashed_password = get_password_hash(password)
    
    # Insere novo usuário no banco
    insert_query = text("""
        INSERT INTO usuarios (username, password) 
        VALUES (:username, :password)
    """)
    db.execute(insert_query, {"username": username, "password": hashed_password})
    db.commit()
    
    return {"username": username, "message": "User created successfully"}

# Função para criar token de acesso JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    # Define tempo de expiração (personalizado ou padrão)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    # Gera token assinado
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# Função para criar refresh token JWT
def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    # Define tempo de expiração mais longo para refresh token
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# Função para obter usuário atual a partir do token
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodifica token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # Obtém username do payload
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Verifica se usuário existe no banco
    query = text("SELECT username FROM usuarios WHERE username = :username")
    user = db.execute(query, {"username": username}).fetchone()
    
    if user is None:
        raise credentials_exception
    
    return user

# Função para autenticar usuário (verifica credenciais)
def authenticate_user(db: Session, username: str, password: str):
    query = text("SELECT username, password FROM usuarios WHERE username = :username")
    result = db.execute(query, {"username": username}).fetchone()
    
    if not result:
        return False  # Usuário não encontrado
    
    if not verify_password(password, result.password):
        return False  # Senha incorreta
        
    return result  # Autenticação bem-sucedida

# Função para renovar access token usando refresh token
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        query = text("SELECT username FROM usuarios WHERE username = :username")
        user = db.execute(query, {"username": username}).fetchone()
        if user is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Gera novo access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    
    # Gera novo refresh token
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)  # Defina isso nas configurações
    new_refresh_token = create_access_token(  # Ou use uma função create_refresh_token se tiver
        data={"sub": username}, expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

# Função para deletar usuário
def delete_user(db: Session, id: int):
    # Primeiro verifica se o usuário existe
    check_query = text("SELECT id FROM usuarios WHERE id = :id")
    user_exists = db.execute(check_query, {"id": id}).fetchone()
    
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Executa deleção
        delete_query = text("DELETE FROM usuarios WHERE id = :id")
        result = db.execute(delete_query, {"id": id})
        db.commit()
        
        # Verifica se usuário foi realmente deletado
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or already deleted"
            )
            
        return {"message": "User deleted successfully"}
    
    except Exception as e:
        # Em caso de erro, faz rollback e retorna erro 500
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )