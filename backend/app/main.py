from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.core.contadores import contador_iniciais
from app.db import Base, SessionLocal, engine
from app.models.user import User
from app.services import em_alta as service_em_alta
from app.services import tags as service_tags
from app.services.decisoes import reconstruir_jornada
from app.routers import auth, decisoes, feed, follows, historias, likes, posts, tags, users, comentarios, em_alta


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
