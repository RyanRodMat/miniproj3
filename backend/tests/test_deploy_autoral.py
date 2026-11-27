"""Deploy (issue #16): seed no boot e CORS configurável por variável de ambiente."""

from fastapi.testclient import TestClient


def test_seed_on_boot_popula_a_rede_e_nao_duplica(monkeypatch):
    from app.db import Base, engine
    from app.main import app

    Base.metadata.drop_all(engine)
    monkeypatch.setenv("SEED_ON_BOOT", "true")

    with TestClient(app) as c:
        r = c.post("/auth/login", json={"username": "mari_nanquim", "password": "quadrinhos-123"})
        assert r.status_code == 200
        h = {"Authorization": f"Bearer {r.json()['token']}"}
        total = c.get("/usuarios", headers=h).json()["total"]
        assert total >= 20
        assert c.get("/em-alta", headers=h).json()["total"] > 0  # core/ reconstruído depois do seed

    with TestClient(app) as c:  # segundo boot: idempotente
        r = c.post("/auth/login", json={"username": "mari_nanquim", "password": "quadrinhos-123"})
        h = {"Authorization": f"Bearer {r.json()['token']}"}
        assert c.get("/usuarios", headers=h).json()["total"] == total


def test_sem_seed_on_boot_o_banco_comeca_vazio(client):
    r = client.post("/auth/login", json={"username": "mari_nanquim", "password": "quadrinhos-123"})
    assert r.status_code == 401


def test_cors_aceita_a_url_publica_do_front(monkeypatch):
    from app.main import _origens_permitidas

    assert _origens_permitidas() == ["http://localhost:3000"]
    monkeypatch.setenv("CORS_ORIGINS", "https://marte.vercel.app/, https://outro.vercel.app")
    assert _origens_permitidas() == [
        "http://localhost:3000",
        "https://marte.vercel.app",
        "https://outro.vercel.app",
    ]


def test_cors_responde_para_o_front_publico(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://marte.vercel.app")
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from app.main import _origens_permitidas

    app = FastAPI()
    app.add_middleware(CORSMiddleware, allow_origins=_origens_permitidas(), allow_methods=["*"], allow_headers=["*"])

    @app.get("/x")
    def x():
        return {}

    r = TestClient(app).get("/x", headers={"Origin": "https://marte.vercel.app"})
    assert r.headers["access-control-allow-origin"] == "https://marte.vercel.app"
    r = TestClient(app).get("/x", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in r.headers
