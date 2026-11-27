from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.post import AutorOut


class ComentarioIn(BaseModel):
    texto: str = Field(min_length=1, max_length=2000)

    @field_validator("texto")
    @classmethod
    def _sem_so_espacos(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("o comentário não pode ser vazio")
        return v


class ComentarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int | None
    capitulo_id: int | None
    autor_id: int
    autor: AutorOut
    texto: str
    criado_em: datetime


class ComentarioPage(BaseModel):
    items: list[ComentarioOut]
    total: int
    offset: int
    limit: int