"""Rotas de autenticação: registro, login e quem sou eu.

Caminho no projeto: backend/app/routers/auth.py
Registrar em main.py:  app.include_router(auth.router)
"""
import secrets

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from app.db import get_db
from app.deps import get_current_user
from app.models.session import Session
from app.models.user import User
from app.schemas.auth import LoginIn, RegistroIn, TokenOut
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

# bcrypt só aceita senhas de até 72 bytes (versões novas levantam ValueError)
MAX_BYTES_SENHA = 72


@router.post("/registro", response_model=UserOut, status_code=201)
def registro(dados: RegistroIn, db: DbSession = Depends(get_db)):
    senha = dados.password.encode()
    if len(senha) > MAX_BYTES_SENHA:
        raise HTTPException(status_code=422, detail="senha longa demais (máx. 72 bytes)")

    if db.scalar(select(User).where(User.username == dados.username)):
        raise HTTPException(status_code=409, detail="username já existe")

    user = User(
        username=dados.username,
        name=dados.name,
        tipo=dados.tipo,  # "artista" ou "leitor", validado pelo schema
        password_hash=bcrypt.hashpw(senha, bcrypt.gensalt()).decode(),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # duas requests com o mesmo username ao mesmo tempo
        db.rollback()
        raise HTTPException(status_code=409, detail="username já existe")
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(dados: LoginIn, db: DbSession = Depends(get_db)):
    erro = HTTPException(status_code=401, detail="usuário ou senha inválidos")

    user = db.scalar(select(User).where(User.username == dados.username))
    # mesma resposta para usuário inexistente, senha errada e hash vazio:
    # não revelar quais usernames existem
    if not user or not user.password_hash:
        raise erro
    try:
        senha_ok = bcrypt.checkpw(dados.password.encode(), user.password_hash.encode())
    except ValueError:  # senha > 72 bytes ou hash malformado
        raise erro
    if not senha_ok:
        raise erro

    sessao = Session(token=secrets.token_urlsafe(32), user_id=user.id)
    db.add(sessao)
    db.commit()
    return {"token": sessao.token}


@router.get("/eu", response_model=UserOut)
def eu(user: User = Depends(get_current_user)):
    return user
