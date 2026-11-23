"""Dependências compartilhadas dos endpoints.

get_current_user é a porta de entrada da autenticação: toda rota protegida
declara `user: User = Depends(get_current_user)`. Ela NÃO vem pronta.
"""

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session as DbSession

from app.db import get_db
from app.models.session import Session
from app.models.user import User


def get_current_user(
    authorization: str | None = Header(default=None),
    db: DbSession = Depends(get_db),
) -> User:
    if authorization and authorization.startswith("Bearer "):
        sessao = db.get(Session, authorization.removeprefix("Bearer "))
        if sessao:
            user = db.get(User, sessao.user_id)
            if user:
                return user
    raise HTTPException(status_code=401, detail="não autenticado")

#Sugestão pra quem for implementar posts de arte
def exige_artista(user: User = Depends(get_current_user)) -> User:
    if user.tipo != "artista":
        raise HTTPException(status_code=403, detail="apenas artistas")
    return user
