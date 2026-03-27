"""Domain model — User"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from .enums import UserRole


class User(BaseModel):
    user_id: str
    nome: str
    email: str
    role: UserRole
    ativo: bool = True
    hashed_password: str


class UserPublic(BaseModel):
    user_id: str
    nome: str
    email: str
    role: UserRole
