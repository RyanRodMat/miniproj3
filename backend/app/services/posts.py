from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate


def criar(db: Session, autor: User, dados: PostCreate) -> Post:
    post = Post(autor_id=autor.id, texto=dados.texto, imagem_url=dados.imagem_url)
    db.add(post)
    db.commit()
    db.refresh(post)
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
    return post


def apagar(db: Session, post: Post) -> None:
    db.delete(post)
    db.commit()


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
