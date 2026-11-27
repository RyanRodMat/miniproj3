from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.capitulo import Capitulo
from app.models.post import Post
from app.routers.auth import get_current_user
from app.schemas.comentario import ComentarioIn, ComentarioOut, ComentarioPage
from app.services import comentarios as service

router = APIRouter(tags=["comentarios"])


@router.post("/posts/{post_id}/comentarios", response_model=ComentarioOut, status_code=201)
def comentar_post(
    post_id: int,
    dados: ComentarioIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    c = service.criar_no_post(db, post_id, user.id, dados.texto)
    if c is None:
        raise HTTPException(404, "Post não encontrado")
    return c


@router.get("/posts/{post_id}/comentarios", response_model=ComentarioPage)
def listar_post(
    post_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if db.get(Post, post_id) is None:
        raise HTTPException(404, "Post não encontrado")
    itens, total = service.listar_do_post(db, post_id, offset, limit)
    return ComentarioPage(items=itens, total=total, offset=offset, limit=limit)


@router.post("/capitulos/{capitulo_id}/comentarios", response_model=ComentarioOut, status_code=201)
def comentar_capitulo(
    capitulo_id: int,
    dados: ComentarioIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    c = service.criar_no_capitulo(db, capitulo_id, user.id, dados.texto)
    if c is None:
        raise HTTPException(404, "Capítulo não encontrado")
    return c


@router.get("/capitulos/{capitulo_id}/comentarios", response_model=ComentarioPage)
def listar_capitulo(
    capitulo_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if db.get(Capitulo, capitulo_id) is None:
        raise HTTPException(404, "Capítulo não encontrado")
    itens, total = service.listar_do_capitulo(db, capitulo_id, offset, limit)
    return ComentarioPage(items=itens, total=total, offset=offset, limit=limit)