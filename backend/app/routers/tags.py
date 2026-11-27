from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.tags import indice_tags, normalizar_tag
from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.routers.posts import _com_curtidas_em_lote
from app.schemas.post import PostPage
from app.schemas.tags import TagsOut
from app.services import tags as service

router = APIRouter(tags=["tags"])


def _tag_ou_422(bruta: str) -> str:
    tag = normalizar_tag(bruta)
    if tag is None:
        raise HTTPException(status_code=422, detail="tag inválida: use [a-z0-9_]+")
    return tag


@router.get("/tags", response_model=TagsOut)
def tags_mais_usadas(
    limit: int = Query(default=20, ge=1, le=100),
    _: User = Depends(get_current_user),
):
    """Chips do Explorar e do onboarding: tags mais usadas, saídas do índice do core/."""
    return TagsOut(
        items=[{"tag": t, "contagem": c} for t, c in indice_tags.mais_usadas(limit)]
    )


@router.get("/tags/{tag}/posts", response_model=PostPage)
def posts_da_tag(
    tag: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    posts, total = service.listar_por_ids(
        db, indice_tags.ids_da_tag(_tag_ou_422(tag)), offset, limit
    )
    items = _com_curtidas_em_lote(db, user, posts)
    return PostPage(items=items, total=total, offset=offset, limit=limit)


@router.get("/explorar", response_model=PostPage)
def explorar(
    tag: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sem `tag`: posts de todos, com as tags de interesse do usuário primeiro."""
    filtro = _tag_ou_422(tag) if tag else None
    posts, total = service.explorar(db, user, filtro, offset, limit)
    items = _com_curtidas_em_lote(db, user, posts)
    return PostPage(items=items, total=total, offset=offset, limit=limit)
