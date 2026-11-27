from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import exige_artista, get_current_user
from app.models.user import User
from app.schemas.historia import CapituloCreate, CapituloOut, HistoriaCreate, HistoriaOut
from app.services import historias as service

router = APIRouter(prefix="/historias", tags=["historias"])


@router.post("", response_model=HistoriaOut, status_code=201)
def criar_historia(
    dados: HistoriaCreate,
    user: User = Depends(exige_artista),
    db: Session = Depends(get_db),
):
    return service.detalhe(db, service.criar(db, user, dados))


@router.get("/{historia_id}", response_model=HistoriaOut)
def ver_historia(
    historia_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.detalhe(db, service.buscar(db, historia_id))


@router.post("/{historia_id}/capitulos", response_model=CapituloOut, status_code=201)
def publicar_capitulo(
    historia_id: int,
    dados: CapituloCreate,
    user: User = Depends(exige_artista),
    db: Session = Depends(get_db),
):
    historia = service.buscar(db, historia_id)
    return service.capitulo_out(db, service.publicar_capitulo(db, historia, user, dados))


@router.get("/{historia_id}/capitulos/{numero}", response_model=CapituloOut)
def ver_capitulo(
    historia_id: int,
    numero: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.buscar(db, historia_id)
    return service.capitulo_out(db, service.buscar_capitulo(db, historia_id, numero))
