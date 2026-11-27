from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.forum import (
    ForumCreate,
    ForumOut,
    ForumPage,
    ForumPostCreate,
    ForumPostOut,
    ForumPostPage,
)
from app.services import foruns as service

router = APIRouter(prefix="/foruns", tags=["foruns"])


@router.post("", response_model=ForumOut, status_code=201)
def criar_forum(
    dados: ForumCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.out(db, user, service.criar(db, user, dados))


@router.get("", response_model=ForumPage)
def listar_foruns(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = service.listar(db, user, offset, limit)
    return ForumPage(items=items, total=total, offset=offset, limit=limit)


@router.get("/{forum_id}", response_model=ForumOut)
def ver_forum(
    forum_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.out(db, user, service.buscar(db, forum_id))


@router.post("/{forum_id}/entrar", status_code=204)
def entrar(
    forum_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.entrar(db, user, forum_id)


@router.post("/{forum_id}/sair", status_code=204)
def sair(
    forum_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.sair(db, user, forum_id)


@router.post("/{forum_id}/posts", response_model=ForumPostOut, status_code=201)
def postar(
    forum_id: int,
    dados: ForumPostCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.postar(db, user, forum_id, dados)


@router.get("/{forum_id}/posts", response_model=ForumPostPage)
def listar_posts(
    forum_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    posts, total = service.listar_posts(db, forum_id, offset, limit)
    return ForumPostPage(items=posts, total=total, offset=offset, limit=limit)
