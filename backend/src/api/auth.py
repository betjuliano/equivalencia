"""Application — Auth: JWT-based authentication (Spec.md section 9.5)"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from src.config import settings
from src.domain.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# In-memory demo users (replace with JSON-file user store in production)
DEMO_USERS = {
    "admin": {"user_id": "admin_001", "nome": "Administrador", "email": "admin@ufsm.br",
               "role": UserRole.ADMIN, "password": "admin123"},
    settings.coord_user: {"user_id": "coord_001", "nome": "Coordenador", "email": "coord@ufsm.br",
               "role": UserRole.COORDENACAO, "password": settings.coord_password},
    "secretaria": {"user_id": "sec_001", "nome": "Secretaria", "email": "sec@ufsm.br",
                    "role": UserRole.SECRETARIA, "password": "sec123"},
}


class TokenData(BaseModel):
    user_id: str
    role: UserRole
    nome: str
    email: str


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = DEMO_USERS.get(username)
    if user and user["password"] == password:
        return user
    return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exc
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("user_id")
        if not user_id:
            raise credentials_exc
        return TokenData(
            user_id=user_id,
            role=UserRole(payload.get("role", "consulta")),
            nome=payload.get("nome", ""),
            email=payload.get("email", ""),
        )
    except Exception:
        raise credentials_exc


async def get_current_user_optional(token: str = Depends(oauth2_scheme)) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("user_id")
        if not user_id:
            return None
        return TokenData(
            user_id=user_id,
            role=UserRole(payload.get("role", "consulta")),
            nome=payload.get("nome", ""),
            email=payload.get("email", ""),
        )
    except Exception:
        return None


def require_role(*roles: UserRole):
    async def checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        return current_user
    return checker
