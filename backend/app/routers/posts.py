from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.post import PostCreate, PostOut, PostPage, PostUpdate
from app.services import posts as service
from app.services import follows as service_follows
from app.services import likes as service_likes

router = APIRouter(prefix="/posts", tags=["posts"])


def _com_curtidas(db: Session, user: User, post) -> PostOut:
    """PostOut com a contagem de curtidas e se `user` já curtiu."""
    return PostOut.model_validate(post).model_copy(
        update={
            "curtidas": service_likes.contador(db, post.id),
            "eu_curti": service_likes.eu_curto(db, user, post.id),
            "autor_eu_sigo": service_follows.eu_sigo(db, user, post.autor_id),
        }
    )


@router.post("", response_model=PostOut, status_code=201)
def criar_post(
    dados: PostCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.criar(db, user, dados)


@router.get("", response_model=PostPage)
def listar_posts(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Posts recentes de todo mundo. Provisório: o feed dos seguidos (GET /feed) é outra issue."""
    posts, total = service.listar_recentes(db, offset, limit)
    items = [_com_curtidas(db, user, p) for p in posts]
    return PostPage(items=items, total=total, offset=offset, limit=limit)


@router.get("/{post_id}", response_model=PostOut)
def ver_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _com_curtidas(db, user, service.buscar(db, post_id))


@router.patch("/{post_id}", response_model=PostOut)
def editar_post(
    post_id: int,
    dados: PostUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = service.buscar_do_autor(db, post_id, user)
    return _com_curtidas(db, user, service.atualizar(db, post, dados))


@router.delete("/{post_id}", status_code=204)
def apagar_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.apagar(db, service.buscar_do_autor(db, post_id, user))
