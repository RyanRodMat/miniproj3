from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.schemas.post import URL_PATTERN

UrlStr = Annotated[str, Field(max_length=300, pattern=URL_PATTERN)]


class DecisaoCreate(BaseModel):
    pergunta: str = Field(min_length=1, max_length=300)
    opcoes: list[str] = Field(min_length=2, max_length=4)
    prazo: datetime

    @field_validator("opcoes")
    @classmethod
    def _opcoes_validas(cls, v: list[str]) -> list[str]:
        v = [o.strip() for o in v]
        if any(not o or len(o) > 100 for o in v):
            raise ValueError("cada opção precisa ter de 1 a 100 caracteres")
        return v

    @field_validator("prazo")
    @classmethod
    def _prazo_em_utc(cls, v: datetime) -> datetime:
        # guardamos UTC sem fuso; um prazo sem fuso é lido como UTC
        if v.tzinfo is not None:
            v = v.astimezone(timezone.utc).replace(tzinfo=None)
        return v


class VotoIn(BaseModel):
    opcao: int


class OpcaoOut(BaseModel):
    texto: str
    votos: int


class DecisaoOut(BaseModel):
    id: int
    capitulo_id: int
    pergunta: str
    opcoes: list[OpcaoOut]
    total_votos: int
    ja_votei: bool
    minha_opcao: int | None
    encerrada: bool
    vencedora: int | None
    prazo: datetime


class CapituloCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    # None só no primeiro capítulo; os seguintes nascem da opção vencedora do anterior
    opcao_origem: int | None = None
    pai_id: int | None = None
    texto: str = Field(default="", max_length=4000)
    # imagens do capítulo, em ordem (o upload é outra issue: aqui só a URL)
    paginas: list[UrlStr] = Field(default_factory=list, max_length=100)


class CapituloOut(BaseModel):
    id: int
    historia_id: int
    numero: int
    titulo: str
    pai_id: int | None
    opcao_origem: int | None


class OpcaoJornadaOut(BaseModel):
    indice: int
    texto: str
    votos: int
    escolhida: bool


class DecisaoJornadaOut(BaseModel):
    id: int
    pergunta: str
    prazo: datetime
    encerrada: bool
    opcoes: list[OpcaoJornadaOut]  # as não escolhidas são "o que poderia ter sido"


class PassoOut(BaseModel):
    capitulo_id: int
    numero: int
    titulo: str
    decisao: DecisaoJornadaOut | None


class JornadaOut(BaseModel):
    historia_id: int
    titulo: str
    caminho: list[PassoOut]
