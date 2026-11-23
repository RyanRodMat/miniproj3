from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.contadores import contador_iniciais
from app.models.user import User
from app.schemas.user import PerfilOut, UserCreate, UserOut
from app.services import follows


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


def perfil(db: Session, viewer: User, username: str) -> PerfilOut:
    user = db.scalar(select(User).where(User.username == username))
    if not user:
        raise HTTPException(status_code=404, detail="usuário não encontrado")
    seguidores, seguindo = follows.contadores(db, user.id)
    return PerfilOut.model_validate(
        {
            **{c: getattr(user, c) for c in UserOut.model_fields},
            "seguidores": seguidores,
            "seguindo": seguindo,
            "eu_sigo": follows.eu_sigo(db, viewer, user.id),
        }
    )
