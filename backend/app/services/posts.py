from fastapi import HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.em_alta import em_alta
from app.core.tags import indice_tags
from app.models.comentario import Comentario
from app.models.follow import Follow
from app.models.like import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate
from app.services import em_alta as service_em_alta
from app.services import tags as service_tags


def criar(db: Session, autor: User, dados: PostCreate) -> Post:
    post = Post(autor_id=autor.id, texto=dados.texto, imagem_url=dados.imagem_url)
    db.add(post)
    db.commit()
    db.refresh(post)
    service_tags.indexar_post(db, post)
    service_em_alta.registrar_post(post)
    return post


def buscar(db: Session, post_id: int) -> Post:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post não encontrado")
    return post


def buscar_do_autor(db: Session, post_id: int, user: User) -> Post:
    """404 se não existe, 403 se existe mas é de outra pessoa."""
    post = buscar(db, post_id)
    if post.autor_id != user.id:
        raise HTTPException(status_code=403, detail="só o autor mexe no post")
    return post


def atualizar(db: Session, post: Post, dados: PostUpdate) -> Post:
    campos = dados.model_fields_set
    if "texto" in campos:
        if dados.texto is None:
            raise HTTPException(status_code=422, detail="texto não pode ser nulo")
        post.texto = dados.texto
    if "imagem_url" in campos:
        post.imagem_url = dados.imagem_url
    db.commit()
    db.refresh(post)
    service_tags.indexar_post(db, post)
    return post


def apagar(db: Session, post: Post) -> None:
    db.execute(delete(Like).where(Like.liked_post_id == post.id))
    db.execute(delete(Comentario).where(Comentario.post_id == post.id))
    db.delete(post)
    db.commit()
    indice_tags.remover(post.id)
    em_alta.remover(post.id)


def listar_recentes(db: Session, offset: int, limit: int) -> tuple[list[Post], int]:
    """Todos os posts, mais novo primeiro (empate: maior id). Provisório até o Feed."""
    total = db.scalar(select(func.count()).select_from(Post)) or 0
    posts = list(
        db.scalars(
            select(Post)
            .order_by(Post.created_at.desc(), Post.id.desc())
            .offset(offset)
            .limit(limit)
        )
    )
    return posts, total


def listar_do_autor(
    db: Session, autor_id: int, offset: int, limit: int
) -> tuple[list[Post], int]:
    """Posts de um usuário (página de perfil), mais novo primeiro (empate: maior id)."""
    filtro = Post.autor_id == autor_id
    total = db.scalar(select(func.count()).select_from(Post).where(filtro)) or 0
    posts = list(
        db.scalars(
            select(Post)
            .where(filtro)
            .order_by(Post.created_at.desc(), Post.id.desc())
            .offset(offset)
            .limit(limit)
        )
    )
    return posts, total


def listar_feed(db: Session, user: User, offset: int, limit: int) -> tuple[list[Post], int]:
    """Posts de quem `user` segue e de quem os seguidos seguem (não os próprios),
    misturados, mais novo primeiro (empate: maior id)."""
    seguidos = select(Follow.followed_id).where(Follow.follower_id == user.id)
    dos_seguidos = select(Follow.followed_id).where(Follow.follower_id.in_(seguidos))
    filtro = (Post.autor_id.in_(seguidos) | Post.autor_id.in_(dos_seguidos)) & (
        Post.autor_id != user.id
    )
    total = db.scalar(select(func.count()).select_from(Post).where(filtro)) or 0
    posts = list(
        db.scalars(
            select(Post)
            .where(filtro)
            .order_by(Post.created_at.desc(), Post.id.desc())
            .offset(offset)
            .limit(limit)
        )
    )
    return posts, total
