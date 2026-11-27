from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.capitulo import Capitulo
from app.models.comentario import Comentario
from app.models.post import Post


def _criar(db: Session, autor_id: int, texto: str, **alvo) -> Comentario:
    c = Comentario(autor_id=autor_id, texto=texto.strip(), **alvo)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _listar(db: Session, coluna, alvo_id: int, offset: int, limit: int):
    base = select(Comentario).where(coluna == alvo_id)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    itens = db.scalars(
        base.order_by(Comentario.criado_em, Comentario.id).offset(offset).limit(limit)
    ).all()
    return list(itens), total


def criar_no_post(db, post_id, autor_id, texto) -> Comentario | None:
    if db.get(Post, post_id) is None:
        return None
    return _criar(db, autor_id, texto, post_id=post_id)


def criar_no_capitulo(db, capitulo_id, autor_id, texto) -> Comentario | None:
    if db.get(Capitulo, capitulo_id) is None:
        return None
    return _criar(db, autor_id, texto, capitulo_id=capitulo_id)


def listar_do_post(db, post_id, offset=0, limit=20):
    return _listar(db, Comentario.post_id, post_id, offset, limit)


def listar_do_capitulo(db, capitulo_id, offset=0, limit=20):
    return _listar(db, Comentario.capitulo_id, capitulo_id, offset, limit)