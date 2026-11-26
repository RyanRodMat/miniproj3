"""Rotas mínimas de história/capítulo, só o necessário para a Jornada funcionar.
A issue de Quadrinhos (#10) substitui/estende este arquivo."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import exige_artista, get_current_user
from app.models.historia import Historia
from app.models.user import User
from app.schemas.jornada import (
    CapituloCreate,
    CapituloOut,
    HistoriaCreate,
    HistoriaOut,
    JornadaOut,
)
from app.services import decisoes as service

router = APIRouter(prefix="/historias", tags=["jornada"])


@router.post("", response_model=HistoriaOut, status_code=201)
def criar_historia(
    dados: HistoriaCreate,
    user: User = Depends(exige_artista),
    db: Session = Depends(get_db),
):
    historia = Historia(titulo=dados.titulo, autor_id=user.id)
    db.add(historia)
    db.commit()
    return HistoriaOut(id=historia.id, titulo=historia.titulo, autor_id=historia.autor_id)


@router.post("/{historia_id}/capitulos", response_model=CapituloOut, status_code=201)
def criar_capitulo(
    historia_id: int,
    dados: CapituloCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.criar_capitulo(db, user, historia_id, dados)


@router.get("/{historia_id}/jornada", response_model=JornadaOut)
def jornada(
    historia_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.montar_jornada(db, historia_id)
