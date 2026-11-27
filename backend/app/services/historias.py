import re

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.historia import Capitulo, Historia, Pagina
from app.models.post import Post
from app.models.user import User
from app.schemas.historia import (
    CapituloCreate,
    CapituloOut,
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
    if not tags:
        raise HTTPException(status_code=422, detail="informe ao menos uma tag")
    historia = Historia(
        autor_id=autor.id,
        titulo=dados.titulo,
        sinopse=dados.sinopse,
        capa_url=dados.capa_url,
        tag=tags[0],
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
            .order_by(Capitulo.ordem)
        )
    )


def detalhe(db: Session, historia: Historia) -> HistoriaOut:
    """História com a lista de capítulos em ordem (sem as páginas)."""
    tags = [t for t in historia.tags.split(",") if t] or [historia.tag]
    return HistoriaOut(
        id=historia.id,
        titulo=historia.titulo,
        sinopse=historia.sinopse,
        capa_url=historia.capa_url,
        tags=tags,
        autor=historia.autor,
        created_at=historia.created_at,
        capitulos=[
            CapituloResumo(id=c.id, numero=c.ordem, titulo=c.titulo)
            for c in _capitulos(db, historia.id)
        ],
    )


def publicar_capitulo(
    db: Session, historia: Historia, autor: User, dados: CapituloCreate
) -> Capitulo:
    """Cria o capítulo (número = próximo da história) e o post "novo capítulo" no feed."""
    if historia.autor_id != autor.id:
        raise HTTPException(status_code=403, detail="só o autor publica capítulos")
    ultimo = db.scalar(
        select(func.max(Capitulo.ordem)).where(Capitulo.historia_id == historia.id)
    )
    capitulo = Capitulo(
        historia_id=historia.id,
        ordem=(ultimo or 0) + 1,
        titulo=dados.titulo,
        texto=dados.texto,
        imagem_url=dados.paginas[0],
    )
    db.add(capitulo)
    db.flush()
    db.add_all(
        Pagina(capitulo_id=capitulo.id, ordem=i, imagem_url=url)
        for i, url in enumerate(dados.paginas, start=1)
    )
    db.add(
        Post(
            autor_id=autor.id,
            texto=f"Novo capítulo de {historia.titulo}: {capitulo.titulo}",
            imagem_url=dados.paginas[0],
            historia_id=historia.id,
        )
    )
    db.commit()
    db.refresh(capitulo)
    return capitulo


def capitulo_out(db: Session, capitulo: Capitulo) -> CapituloOut:
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
    return CapituloOut(
        id=capitulo.id,
        historia_id=capitulo.historia_id,
        numero=capitulo.ordem,
        titulo=capitulo.titulo,
        texto=capitulo.texto,
        paginas=paginas,
    )


def buscar_capitulo(db: Session, historia_id: int, numero: int) -> Capitulo:
    capitulo = db.scalar(
        select(Capitulo).where(
            Capitulo.historia_id == historia_id, Capitulo.ordem == numero
        )
    )
    if not capitulo:
        raise HTTPException(status_code=404, detail="capítulo não encontrado")
    return capitulo
