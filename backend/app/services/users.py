from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.contadores import contador_iniciais
from app.models.user import User
from app.schemas.user import PerfilUpdate, UserCreate


def listar(db: Session, offset: int, limit: int) -> tuple[list[User], int]:
    total = db.scalar(select(func.count()).select_from(User)) or 0
    users = list(
        db.scalars(
            select(User).order_by(User.username).offset(offset).limit(limit)
        )
    )
    return users, total


def criar(db: Session, dados: UserCreate) -> User:
    ja_existe = db.scalar(select(User).where(User.username == dados.username))
    if ja_existe:
        raise HTTPException(status_code=409, detail="username já existe")

    user = User(**dados.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)

    contador_iniciais.incrementar(user.username)
    return user


def buscar_por_username(db: Session, username: str) -> User:
    user = db.scalar(select(User).where(User.username == username))
    if not user:
        raise HTTPException(status_code=404, detail="usuário não encontrado")
    return user


def atualizar_perfil(db: Session, user: User, dados: PerfilUpdate) -> User:
    for campo in dados.model_fields_set:
        valor = getattr(dados, campo)
        if valor is None:
            raise HTTPException(status_code=422, detail=f"{campo} não pode ser nulo")
        setattr(user, campo, valor)
    db.commit()
    db.refresh(user)
    return user
