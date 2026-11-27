from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.post import AutorOut


def _limpo(v: str) -> str:
    v = v.strip()
    if not v:
        raise ValueError("não pode ser vazio")
    return v


class ForumCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=60)
    descricao: str = Field(default="", max_length=300)

    _nome_limpo = field_validator("nome")(lambda cls, v: _limpo(v))

    @field_validator("descricao")
    @classmethod
    def _descricao_limpa(cls, v: str) -> str:
        return v.strip()


class ForumOut(BaseModel):
    id: int
    nome: str
    descricao: str
    criador_id: int
    created_at: datetime
    membros: int = 0
    sou_membro: bool = False


class ForumPage(BaseModel):
    items: list[ForumOut]
    total: int
    offset: int
    limit: int


class ForumPostCreate(BaseModel):
    texto: str = Field(min_length=1, max_length=2000)

    _texto_limpo = field_validator("texto")(lambda cls, v: _limpo(v))


class ForumPostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    forum_id: int
    texto: str
    autor: AutorOut
    created_at: datetime


class ForumPostPage(BaseModel):
    items: list[ForumPostOut]
    total: int
    offset: int
    limit: int
