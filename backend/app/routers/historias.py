"""Histórias: criação, página da história, leitor de capítulo e a jornada (votação)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import exige_artista, get_current_user
from app.models.user import User
from app.schemas.historia import CapituloDetalhe, HistoriaCreate, HistoriaOut
from app.schemas.jornada import CapituloCreate, CapituloOut, JornadaOut
from app.services import decisoes as service_jornada
from app.services import historias as service

router = APIRouter(prefix="/historias", tags=["historias"])


@router.post("", response_model=HistoriaOut, status_code=201)
def criar_historia(
    dados: HistoriaCreate,
    user: User = Depends(exige_artista),
    db: Session = Depends(get_db),
):
    return service.detalhe(db, service.criar(db, user, dados))


@router.get("", response_model=list[HistoriaOut])
def listar_historias(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.listar(db)


@router.get("/{historia_id}", response_model=HistoriaOut)
def ver_historia(
    historia_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.detalhe(db, service.buscar(db, historia_id))


@router.post("/{historia_id}/capitulos", response_model=CapituloOut, status_code=201)
def criar_capitulo(
    historia_id: int,
    dados: CapituloCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service_jornada.criar_capitulo(db, user, historia_id, dados)


@router.get("/{historia_id}/capitulos/{numero}", response_model=CapituloDetalhe)
def ver_capitulo(
    historia_id: int,
    numero: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.buscar(db, historia_id)
    return service.capitulo_detalhe(db, service.buscar_capitulo(db, historia_id, numero))


@router.get("/{historia_id}/jornada", response_model=JornadaOut)
def jornada(
    historia_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service_jornada.montar_jornada(db, historia_id)
