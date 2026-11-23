from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.follow import Follow
from app.models.user import User


def _alvo(db: Session, username: str) -> User:
    alvo = db.scalar(select(User).where(User.username == username))
    if not alvo:
        raise HTTPException(status_code=404, detail="usuário não encontrado")
    return alvo


def _segue(db: Session, follower_id: int, followed_id: int) -> bool:
    return db.get(Follow, (follower_id, followed_id)) is not None


def seguir(db: Session, user: User, username: str) -> None:
    alvo = _alvo(db, username)
    if alvo.id == user.id:
        raise HTTPException(status_code=422, detail="não dá para seguir a si mesmo")
    if _segue(db, user.id, alvo.id):
        return  # idempotente
    db.add(Follow(follower_id=user.id, followed_id=alvo.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()  # duas requests simultâneas: a outra já criou, e está tudo bem


def deixar_de_seguir(db: Session, user: User, username: str) -> None:
    alvo = _alvo(db, username)
    follow = db.get(Follow, (user.id, alvo.id))
    if follow:
        db.delete(follow)
        db.commit()


def contadores(db: Session, user_id: int) -> tuple[int, int]:
    """(seguidores, seguindo)"""
    seguidores = db.scalar(
        select(func.count()).select_from(Follow).where(Follow.followed_id == user_id)
    )
    seguindo = db.scalar(
        select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
    )
    return seguidores or 0, seguindo or 0


def eu_sigo(db: Session, user: User, alvo_id: int) -> bool:
    return _segue(db, user.id, alvo_id)
