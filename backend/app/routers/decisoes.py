from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.jornada import DecisaoCreate, DecisaoOut, VotoIn
from app.services import decisoes as service

router = APIRouter(tags=["jornada"])


@router.post("/capitulos/{capitulo_id}/decisao", response_model=DecisaoOut, status_code=201)
def criar_decisao(
    capitulo_id: int,
    dados: DecisaoCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.criar_decisao(db, user, capitulo_id, dados)


@router.post("/decisoes/{decisao_id}/votar", response_model=DecisaoOut)
def votar(
    decisao_id: int,
    dados: VotoIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.votar(db, user, decisao_id, dados.opcao)


@router.get("/decisoes/{decisao_id}", response_model=DecisaoOut)
def obter(
    decisao_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.obter(db, user, decisao_id)
