import re

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.capitulo import Capitulo
from app.models.historia import Historia
from app.models.pagina import Pagina
from app.models.user import User
from app.schemas.historia import (
    CapituloDetalhe,
    CapituloResumo,
    HistoriaCreate,
    HistoriaOut,
)


def normalizar_tags(tags: list[str]) -> list[str]:
    """minúsculas, sem espaços nas pontas, sem vazio nem repetida (mantém a ordem)."""
    vistas: dict[str, None] = {}
    for t in tags:
        t = re.sub(r"\s+", "_", t.strip().lower().lstrip("#"))
        if t:
            vistas.setdefault(t[:30])
    return list(vistas)


def criar(db: Session, autor: User, dados: HistoriaCreate) -> Historia:
    tags = normalizar_tags(dados.tags)
    historia = Historia(
        autor_id=autor.id,
        titulo=dados.titulo,
        sinopse=dados.sinopse,
        capa_url=dados.capa_url,
        tag=tags[0] if tags else "",
        tags=",".join(tags),
    )
    db.add(historia)
    db.commit()
    db.refresh(historia)
    return historia


def buscar(db: Session, historia_id: int) -> Historia:
    historia = db.get(Historia, historia_id)
    if not historia:
        raise HTTPException(status_code=404, detail="história não encontrada")
    return historia


def _capitulos(db: Session, historia_id: int) -> list[Capitulo]:
    return list(
        db.scalars(
            select(Capitulo)
            .where(Capitulo.historia_id == historia_id)
            .order_by(Capitulo.numero)
        )
    )


def detalhe(db: Session, historia: Historia) -> HistoriaOut:
    """História com a lista de capítulos em ordem (sem as páginas)."""
    tags = [t for t in historia.tags.split(",") if t] or ([historia.tag] if historia.tag else [])
    return HistoriaOut(
        id=historia.id,
        titulo=historia.titulo,
        sinopse=historia.sinopse,
        capa_url=historia.capa_url,
        tags=tags,
        autor=historia.autor,
        created_at=historia.created_at,
        capitulos=[
            CapituloResumo(id=c.id, numero=c.numero, titulo=c.titulo)
            for c in _capitulos(db, historia.id)
        ],
    )


def capitulo_detalhe(db: Session, capitulo: Capitulo) -> CapituloDetalhe:
    paginas = list(
        db.scalars(
            select(Pagina.imagem_url)
            .where(Pagina.capitulo_id == capitulo.id)
            .order_by(Pagina.ordem)
        )
    )
    # capítulo do seed: sem `Pagina`, a imagem única vira a única página
    if not paginas and capitulo.imagem_url:
        paginas = [capitulo.imagem_url]
    return CapituloDetalhe(
        id=capitulo.id,
        historia_id=capitulo.historia_id,
        numero=capitulo.numero,
        titulo=capitulo.titulo,
        texto=capitulo.texto,
        paginas=paginas,
    )


def buscar_capitulo(db: Session, historia_id: int, numero: int) -> Capitulo:
    capitulo = db.scalar(
        select(Capitulo).where(
            Capitulo.historia_id == historia_id, Capitulo.numero == numero
        )
    )
    if not capitulo:
        raise HTTPException(status_code=404, detail="capítulo não encontrado")
    return capitulo
