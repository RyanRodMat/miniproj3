from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[a-z0-9_]+$")
    name: str = Field(min_length=1, max_length=80)
    bio: str = Field(default="", max_length=280)
    avatar_url: str = Field(default="", max_length=300)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str
    bio: str
    avatar_url: str
    tipo: Literal["artista", "leitor"]
    created_at: datetime

class PerfilOut(UserOut):
    """GET /usuarios/{username}: o usuário + contadores de follow."""

    seguidores: int
    seguindo: int
    eu_sigo: bool  # o usuário logado já segue este perfil? (botão seguir/deixar de seguir)


class UserPage(BaseModel):
    """Padrão de paginação do projeto: todo endpoint de listagem devolve isto."""

    items: list[UserOut]
    total: int
    offset: int
    limit: int
