from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.post import URL_PATTERN, AutorOut

UrlStr = Annotated[str, Field(max_length=300, pattern=URL_PATTERN)]


class HistoriaCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=120)
    sinopse: str = Field(default="", max_length=500)
    capa_url: str | None = Field(default=None, max_length=300, pattern=URL_PATTERN)
    tags: list[str] = Field(min_length=1, max_length=5)


class CapituloCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=120)
    texto: str = Field(default="", max_length=4000)
    paginas: list[UrlStr] = Field(min_length=1, max_length=100)


class CapituloResumo(BaseModel):
    id: int
    numero: int
    titulo: str


class CapituloOut(CapituloResumo):
    historia_id: int
    texto: str
    paginas: list[str]


class HistoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    sinopse: str
    capa_url: str | None
    tags: list[str]
    autor: AutorOut
    created_at: datetime
    capitulos: list[CapituloResumo]
