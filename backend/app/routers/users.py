"""Slice de exemplo completo: model → schema → service → router → página Next.

Toda feature nova imita este caminho. 1 arquivo por router — registre o seu
com uma linha em main.py.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.contadores import contador_iniciais
from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.post import PostPage
from app.schemas.user import PerfilOut, PerfilUpdate, UserCreate, UserOut, UserPage
from app.services import follows as service_follows
from app.services import posts as service_posts
from app.services import users as service

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=UserPage)
def listar_usuarios(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    users, total = service.listar(db, offset, limit)
    return UserPage(items=users, total=total, offset=offset, limit=limit)


@router.get("/stats")
def stats_por_inicial():
    """Endpoint que USA a estrutura do core/ — alvo do teste-sabotagem de exemplo."""
    return {"usuarios_por_inicial": contador_iniciais.contagem()}


@router.post("", response_model=UserOut, status_code=201)
def criar_usuario(dados: UserCreate, db: Session = Depends(get_db)):
    # ponytail: criação sem senha — o guia de auth evolui isto para o registro real
    return service.criar(db, dados)


@router.patch("/eu", response_model=UserOut)
def editar_meu_perfil(
    dados: PerfilUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.atualizar_perfil(db, user, dados)


# Antes de "/{username}", senão "eu" seria lido como username.
@router.get("/eu/seguindo")
def meus_seguidos(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Usernames que o usuário logado segue (a lista de usuários usa para o botão seguir)."""
    return {"usernames": service_follows.usernames_seguidos(db, user)}


@router.get("/eu/seguindo/perfis", response_model=list[UserOut])
def meus_seguidos_perfis(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Quem o usuário logado segue, com nome e avatar (a barra lateral usa)."""
    return service_follows.usuarios_seguidos(db, user)


# Declarada depois de /stats: "/{username}" casaria com "stats" se viesse antes.
@router.get("/{username}", response_model=PerfilOut)
def ver_perfil(
    username: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.perfil(db, user, username)


@router.get("/{username}/posts", response_model=PostPage)
def posts_do_usuario(
    username: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Posts do perfil, mais novo primeiro, paginados como todas as listagens."""
    autor = service.buscar(db, username)
    posts, total = service_posts.listar_do_autor(db, autor.id, offset, limit)
    return PostPage(items=posts, total=total, offset=offset, limit=limit)
