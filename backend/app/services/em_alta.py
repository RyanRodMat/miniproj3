import time
from datetime import timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.em_alta import em_alta
from app.models.capitulo import Capitulo
from app.models.comentario import Comentario
from app.models.decisao import Decisao
from app.models.like import Like
from app.models.post import Post
from app.models.voto import Voto


def _epoch(dt) -> float:
    """O SQLite devolve datetimes sem fuso; tudo no banco é UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def registrar_post(post: Post) -> None:
    em_alta.registrar(post.id, _epoch(post.created_at), post.historia_id)


def reconstruir(db: Session) -> None:
    """Startup: refaz os contadores a partir do banco. O(n)."""
    curtidas = dict(
        db.execute(select(Like.liked_post_id, func.count()).group_by(Like.liked_post_id)).all()
    )
    comentarios = dict(
        db.execute(
            select(Comentario.post_id, func.count())
            .where(Comentario.post_id.is_not(None))
            .group_by(Comentario.post_id)
        ).all()
    )
    votos = dict(
        db.execute(
            select(Capitulo.historia_id, func.count())
            .select_from(Voto)
            .join(Decisao, Decisao.id == Voto.decisao_id)
            .join(Capitulo, Capitulo.id == Decisao.capitulo_id)
            .group_by(Capitulo.historia_id)
        ).all()
    )
    em_alta.reconstruir(
        [
            (p.id, _epoch(p.created_at), p.historia_id, curtidas.get(p.id, 0), comentarios.get(p.id, 0))
            for p in db.scalars(select(Post))
        ],
        votos,
    )


def listar(db: Session, offset: int, limit: int) -> tuple[list[Post], int]:
    """Página do ranking Em alta, do mais quente para o menos."""
    ids = em_alta.top(offset + limit, time.time())[offset:]
    posts = {p.id: p for p in db.scalars(select(Post).where(Post.id.in_(ids)))}
    return [posts[i] for i in ids if i in posts], len(em_alta)
