from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.routers.posts import _com_curtidas_em_lote
from app.schemas.post import PostPage
from app.services import em_alta as service

router = APIRouter(prefix="/em-alta", tags=["em-alta"])


@router.get("", response_model=PostPage)
def em_alta(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Posts por engajamento recente (ver core/em_alta.py), não por quem você segue."""
    posts, total = service.listar(db, offset, limit)
    items = _com_curtidas_em_lote(db, user, posts)
    return PostPage(items=items, total=total, offset=offset, limit=limit)
