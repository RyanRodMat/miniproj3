from pydantic import BaseModel


class TagContagem(BaseModel):
    tag: str
    contagem: int


class TagsOut(BaseModel):
    items: list[TagContagem]
