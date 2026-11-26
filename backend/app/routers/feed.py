from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.routers.posts import _com_curtidas
from app.schemas.post import PostPage
from app.services import posts as service

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("", response_model=PostPage)
def feed(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Feed cronológico: só posts de quem o usuário segue, mais novo primeiro."""
    posts, total = service.listar_feed(db, user, offset, limit)
    items = [_com_curtidas(db, user, p) for p in posts]
    return PostPage(items=items, total=total, offset=offset, limit=limit)
