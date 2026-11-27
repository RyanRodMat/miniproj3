"""Comentários em capítulos (issue #7)."""

HIST = {"titulo": "Torre Torta", "sinopse": "s", "tags": ["fantasia"]}
CAP = {"titulo": "O começo", "texto": "t", "paginas": ["/uploads/p1.png"]}


def _artista(client, username):
    r = client.post(
        "/auth/registro",
        json={"username": username, "name": "A", "password": "senha-forte-123", "tipo": "artista"},
    )
    assert r.status_code == 201
    r = client.post("/auth/login", json={"username": username, "password": "senha-forte-123"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _capitulo(client, autor):
    hid = client.post("/historias", json=HIST, headers=autor).json()["id"]
    r = client.post(f"/historias/{hid}/capitulos", json=CAP, headers=autor)
    assert r.status_code == 201
    return r.json()["id"]


def test_comentarios_do_capitulo_em_ordem_cronologica(client, logar):
    ana = _artista(client, "ana")
    bia = logar("bia")
    cid = _capitulo(client, ana)

    r1 = client.post(f"/capitulos/{cid}/comentarios", json={"texto": "primeiro!"}, headers=bia)
    assert r1.status_code == 201
    assert r1.json()["capitulo_id"] == cid
    assert r1.json()["post_id"] is None
    client.post(f"/capitulos/{cid}/comentarios", json={"texto": "segundo"}, headers=ana)

    r = client.get(f"/capitulos/{cid}/comentarios", headers=ana)
    assert r.status_code == 200
    assert [c["texto"] for c in r.json()["items"]] == ["primeiro!", "segundo"]
    assert r.json()["total"] == 2


def test_comentarios_de_capitulo_e_post_nao_se_misturam(client, logar):
    ana = _artista(client, "ana")
    bia = logar("bia")
    cid = _capitulo(client, ana)
    pid = client.post("/posts", json={"texto": "um post"}, headers=ana).json()["id"]

    client.post(f"/capitulos/{cid}/comentarios", json={"texto": "no capítulo"}, headers=bia)
    client.post(f"/posts/{pid}/comentarios", json={"texto": "no post"}, headers=bia)

    cap = client.get(f"/capitulos/{cid}/comentarios", headers=ana).json()["items"]
    post = client.get(f"/posts/{pid}/comentarios", headers=ana).json()["items"]
    assert [c["texto"] for c in cap] == ["no capítulo"]
    assert [c["texto"] for c in post] == ["no post"]


def test_capitulo_inexistente_e_sem_login(client, logar):
    bia = logar("bia")
    assert client.post("/capitulos/99999/comentarios", json={"texto": "oi"}, headers=bia).status_code == 404
    assert client.get("/capitulos/99999/comentarios", headers=bia).status_code == 404
    assert client.get("/capitulos/1/comentarios").status_code == 401