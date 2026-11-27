from sqlalchemy import case, delete, func, select
from sqlalchemy.orm import Session

from app.core.tags import extrair_tags, indice_tags, normalizar_tag
from app.models.historia import Historia
from app.models.interesse import Interesse
from app.models.post import Post
from app.models.user import User

MAX_TAGS_INTERESSE = 10


def _tags_da_historia(historia: Historia | None) -> list[str]:
    if historia is None:
        return []
    brutas = [t for t in historia.tags.split(",") if t] or [historia.tag]
    return [t for t in (normalizar_tag(b) for b in brutas) if t]


def tags_do_post(post: Post, historia: Historia | None) -> list[str]:
    """#tags do texto + tags da história (posts de "novo capítulo"), sem repetir."""
    return list(dict.fromkeys(extrair_tags(post.texto) + _tags_da_historia(historia)))


def indexar_post(db: Session, post: Post) -> None:
    historia = db.get(Historia, post.historia_id) if post.historia_id else None
    indice_tags.indexar(post.id, tags_do_post(post, historia))


def reconstruir(db: Session) -> None:
    """Startup: reconstrói o índice a partir dos posts (e tags das histórias)."""
    historias = {h.id: h for h in db.scalars(select(Historia))}
    indice_tags.reconstruir(
        [
            (p.id, tags_do_post(p, historias.get(p.historia_id)))
            for p in db.scalars(select(Post))
        ]
    )


def tags_de_interesse(db: Session, user: User) -> list[str]:
    return sorted(db.scalars(select(Interesse.tag).where(Interesse.user_id == user.id)))


def definir_interesses(db: Session, user: User, tags: list[str]) -> None:
    """Substitui as tags de interesse do usuário (sem commit: quem chama commita)."""
    db.execute(delete(Interesse).where(Interesse.user_id == user.id))
    for tag in tags:
        db.add(Interesse(user_id=user.id, tag=tag))


def normalizar_interesses(tags: list[str]) -> list[str] | None:
    """Normaliza e tira repetidas; None se alguma for inválida."""
    limpas = [normalizar_tag(t) for t in tags]
    if any(t is None or len(t) > 30 for t in limpas):
        return None
    return list(dict.fromkeys(limpas))  # type: ignore[arg-type]


def listar_por_ids(
    db: Session, ids: set[int], offset: int, limit: int
) -> tuple[list[Post], int]:
    """Posts com esses ids, mais novo primeiro (empate: maior id)."""
    posts = list(
        db.scalars(
            select(Post)
            .where(Post.id.in_(ids))
            .order_by(Post.created_at.desc(), Post.id.desc())
            .offset(offset)
            .limit(limit)
        )
    )
    return posts, len(ids)


def explorar(
    db: Session, user: User, tag: str | None, offset: int, limit: int
) -> tuple[list[Post], int]:
    """Com `tag`: só os posts dela. Sem: todos, priorizando as tags de interesse."""
    if tag:
        return listar_por_ids(db, indice_tags.ids_da_tag(tag), offset, limit)

    total = db.scalar(select(func.count()).select_from(Post)) or 0
    interesse = indice_tags.ids_com_alguma(tags_de_interesse(db, user))
    ordem = [Post.created_at.desc(), Post.id.desc()]
    if interesse:
        ordem.insert(0, case((Post.id.in_(interesse), 0), else_=1))
    posts = list(db.scalars(select(Post).order_by(*ordem).offset(offset).limit(limit)))
    return posts, total
