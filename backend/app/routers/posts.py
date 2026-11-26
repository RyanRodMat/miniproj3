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


def _com_curtidas_em_lote(db: Session, user: User, posts: list) -> list[PostOut]:
    """PostOut com curtidas, eu_curti e autor_eu_sigo; 3 queries para a página toda."""
    ids = [p.id for p in posts]
    curtidas = service_likes.contadores_em_lote(db, ids)
    curtidos = service_likes.curtidos_em_lote(db, user, ids)
    seguidos = service_follows.seguidos_em_lote(db, user, [p.autor_id for p in posts])
    return [
        PostOut.model_validate(p).model_copy(
            update={
                "curtidas": curtidas.get(p.id, 0),
                "eu_curti": p.id in curtidos,
                "autor_eu_sigo": p.autor_id in seguidos,
            }
        )
        for p in posts
    ]


def _com_curtidas(db: Session, user: User, post) -> PostOut:
    return _com_curtidas_em_lote(db, user, [post])[0]


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
    items = _com_curtidas_em_lote(db, user, posts)
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
