"""API — Auth login endpoint"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from src.api.auth import authenticate_user, create_access_token

router = APIRouter()


@router.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
    token = create_access_token({
        "user_id": user["user_id"],
        "role": user["role"],
        "nome": user["nome"],
        "email": user["email"],
    })
    return {"access_token": token, "token_type": "bearer", "role": user["role"], "nome": user["nome"]}
