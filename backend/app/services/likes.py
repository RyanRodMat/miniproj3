from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.like import Like
from app.models.user import User
from app.models.post import Post

def _alvo(db: Session, post_id: int) -> Post:
    alvo = db.scalar(select(Post).where(Post.id == post_id))
    if not alvo:
        raise HTTPException(status_code=404, detail="post não encontrado")
    return alvo

def _curte(db: Session, liker_id: int, liked_post_id: int) -> bool:
    return db.get(Like, (liker_id, liked_post_id)) is not None

def curtir(db: Session, user: User, post_id: int) -> None:
    # Curtir os próprios posts é permitido, então, não há porque verificar se o post é do 
    # próprio user
    alvo = _alvo(db, post_id)
    if _curte(db, user.id, alvo.id):
        return  # idempotente
    db.add(Like(liker_id=user.id, liked_post_id=alvo.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()  # duas requests simultâneas: a outra já criou, e está tudo bem


def descurtir(db: Session, user: User, post_id: int) -> None:
    alvo = _alvo(db, post_id)
    like = db.get(Like, (user.id, alvo.id))
    if like:
        db.delete(like)
        db.commit()


def contador(db: Session, post_id: int) -> int:
    curtidas = db.scalar(
        select(func.count()).select_from(Like).where(Like.liked_post_id == post_id)
    )
    return curtidas or 0


def eu_curto(db: Session, user: User, alvo_id: int) -> bool:
    return _curte(db, user.id, alvo_id)


