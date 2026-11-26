from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# só http(s) ou caminho do próprio backend (ex.: /uploads/x.png); bloqueia javascript:
URL_PATTERN = r"^(https?://|/)\S+$"


class PostCreate(BaseModel):
    texto: str = Field(min_length=1, max_length=2000)
    imagem_url: str | None = Field(default=None, max_length=300, pattern=URL_PATTERN)


class PostUpdate(BaseModel):
    # campo ausente = não mexe; imagem_url: null = remove a imagem
    texto: str | None = Field(default=None, min_length=1, max_length=2000)
    imagem_url: str | None = Field(default=None, max_length=300, pattern=URL_PATTERN)


class AutorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str
    avatar_url: str
    tipo: Literal["artista", "leitor"]


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    texto: str
    imagem_url: str | None
    autor: AutorOut
    created_at: datetime
    curtidas: int = 0
    eu_curti: bool = False
    autor_eu_sigo: bool = False  # o usuário logado segue o autor? (botão seguir no card)


class PostPage(BaseModel):
    """Padrão de paginação do projeto (igual a UserPage)."""

    items: list[PostOut]
    total: int
    offset: int
    limit: int
