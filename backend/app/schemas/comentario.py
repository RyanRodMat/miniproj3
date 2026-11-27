from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ComentarioIn(BaseModel):
    texto: str = Field(min_length=1, max_length=2000)


class ComentarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int | None
    capitulo_id: int | None
    autor_id: int
    texto: str
    criado_em: datetime


class ComentarioPage(BaseModel):
    items: list[ComentarioOut]
    total: int
    offset: int
    limit: int