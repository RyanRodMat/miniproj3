"""GET /em-alta: ranking por engajamento recente."""


def _artista(client, username):
    client.post(
        "/auth/registro",
        json={"username": username, "name": username, "password": "senha-forte-123", "tipo": "artista"},
    )
    r = client.post("/auth/login", json={"username": username, "password": "senha-forte-123"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _post(client, headers, texto):
    r = client.post("/posts", json={"texto": texto}, headers=headers)
    assert r.status_code == 201
    return r.json()["id"]


def _textos(client, headers, query=""):
    r = client.get(f"/em-alta{query}", headers=headers)
    assert r.status_code == 200
    return [p["texto"] for p in r.json()["items"]]


def test_em_alta_exige_login(client):
    assert client.get("/em-alta").status_code == 401


def test_em_alta_sobe_com_curtidas_e_comentarios(client, logar):
    ana, bia, caio = logar("ana"), logar("bia"), logar("caio")
    a = _post(client, ana, "a")
    b = _post(client, ana, "b")
    c = _post(client, ana, "c")

    client.post(f"/posts/{a}/curtir", headers=bia)
    client.post(f"/posts/{b}/comentarios", json={"texto": "oi"}, headers=bia)
    client.post(f"/posts/{b}/comentarios", json={"texto": "oi 2"}, headers=caio)

    # b: 2 comentários (4); a: 1 curtida (1); c: nada, mas é o mais novo
    assert _textos(client, ana) == ["b", "a", "c"]

    # em alta mostra gente que você NÃO segue (diferente do feed)
    assert client.get("/feed", headers=bia).json()["items"] == []


def test_descurtir_desce_no_ranking(client, logar):
    ana, bia = logar("ana"), logar("bia")
    a = _post(client, ana, "a")
    _post(client, ana, "b")
    client.post(f"/posts/{a}/curtir", headers=bia)
    assert _textos(client, ana) == ["a", "b"]
    client.delete(f"/posts/{a}/curtir", headers=bia)
    assert _textos(client, ana) == ["b", "a"]  # empate: mais novo primeiro


def test_curtida_repetida_nao_conta_duas_vezes(client, logar):
    ana, bia = logar("ana"), logar("bia")
    a = _post(client, ana, "a")
    b = _post(client, ana, "b")
    client.post(f"/posts/{a}/curtir", headers=bia)
    client.post(f"/posts/{a}/curtir", headers=bia)  # idempotente
    client.post(f"/posts/{b}/curtir", headers=ana)
    client.post(f"/posts/{b}/curtir", headers=bia)
    assert _textos(client, ana)[0] == "b"


def test_post_apagado_sai_do_ranking_e_paginacao(client, logar):
    ana = logar("ana")
    ids = [_post(client, ana, f"p{i}") for i in range(5)]
    client.delete(f"/posts/{ids[4]}", headers=ana)

    r = client.get("/em-alta?offset=1&limit=2", headers=ana).json()
    assert r["total"] == 4
    assert [p["texto"] for p in r["items"]] == ["p2", "p1"]
    assert client.get("/em-alta?limit=0", headers=ana).status_code == 422
    assert client.get("/em-alta?offset=50", headers=ana).json()["items"] == []


def test_votos_levantam_o_post_de_novo_capitulo(client, logar):
    from datetime import datetime, timedelta, timezone

    ana = _artista(client, "ana")
    bia = logar("bia")
    hist = client.post("/historias", json={"titulo": "H"}, headers=ana).json()
    cap = client.post(
        f"/historias/{hist['id']}/capitulos", json={"titulo": "1"}, headers=ana
    ).json()
    prazo = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    d = client.post(
        f"/capitulos/{cap['id']}/decisao",
        json={"pergunta": "?", "opcoes": ["x", "y"], "prazo": prazo},
        headers=ana,
    ).json()
    _post(client, ana, "mais novo")
    # sem votos o mais novo lidera; com um voto (peso 3) o post do capítulo passa
    assert _textos(client, ana)[0] == "mais novo"
    client.post(f"/decisoes/{d['id']}/votar", json={"opcao": 0}, headers=bia)
    assert _textos(client, ana)[0].startswith("Novo capítulo")


def test_reconstruir_no_startup_recupera_o_engajamento(client, logar):
    from app.core.em_alta import em_alta
    from app.db import SessionLocal
    from app.services import em_alta as service

    ana, bia = logar("ana"), logar("bia")
    a = _post(client, ana, "a")
    _post(client, ana, "b")
    client.post(f"/posts/{a}/curtir", headers=bia)
    em_alta.reconstruir([], {})  # simula o restart: memória zerada
    with SessionLocal() as db:
        service.reconstruir(db)
    assert _textos(client, ana) == ["a", "b"]
