import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.core.contadores import contador_iniciais
from app.db import Base, SessionLocal, engine
from app.models.user import User
from app.routers import auth, comentarios, decisoes, em_alta, feed, follows, foruns, historias, likes, posts, tags, users
from app.services import em_alta as service_em_alta
from app.services import tags as service_tags
from app.services.decisoes import reconstruir_jornada
from app.services.uploads import UPLOAD_DIR


def _origens_permitidas() -> list[str]:
    """localhost + as URLs públicas do front em CORS_ORIGINS (separadas por vírgula).

    Ex.: CORS_ORIGINS=https://meu-front.vercel.app (guia 08, passo 3)."""
    extras = os.environ.get("CORS_ORIGINS", "")
    return ["http://localhost:3000"] + [o.strip().rstrip("/") for o in extras.split(",") if o.strip()]


def _semear_no_boot() -> None:
    """SEED_ON_BOOT=true: o filesystem do Render zera a cada restart, então a rede
    precisa voltar populada. Idempotente: se o seed já existe, não faz nada."""
    backend = str(Path(__file__).resolve().parents[1])
    if backend not in sys.path:
        sys.path.insert(0, backend)
    from scripts.seed import seed_fake

    with SessionLocal() as db:
        seed_fake(db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    if os.environ.get("SEED_ON_BOOT", "").lower() == "true":
        _semear_no_boot()
    # Reconstrói as estruturas do core/ a partir do banco (memória zera a cada
    # restart — inclusive no --reload; ver core/README.md).
    with SessionLocal() as db:
        usernames = list(db.scalars(select(User.username)))
    contador_iniciais.reconstruir(usernames)
    with SessionLocal() as db:
        reconstruir_jornada(db)
        service_tags.reconstruir(db)
        service_em_alta.reconstruir(db)
    yield


app = FastAPI(title="Rede Social da Trilha", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origens_permitidas(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR.mkdir(exist_ok=True)  # o mount falha se a pasta não existir
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 1 linha por feature — registre o seu router aqui.
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(follows.router)
app.include_router(likes.router)
app.include_router(feed.router)
app.include_router(historias.router)
app.include_router(decisoes.router)
app.include_router(tags.router)
app.include_router(comentarios.router)
app.include_router(em_alta.router)
app.include_router(foruns.router)
