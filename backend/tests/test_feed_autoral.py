def test_feed_cronologico_dos_seguidos(client, logar):
    ana = logar("ana")
    bia = logar("bia")
    caio = logar("caio")  # ana não segue o caio

    client.post("/usuarios/bia/follow", headers=ana)
    for texto, quem in [("bia 1", bia), ("caio 1", caio), ("ana 1", ana), ("bia 2", bia)]:
        client.post("/posts", json={"texto": texto}, headers=quem)

    r = client.get("/feed?offset=0&limit=1", headers=ana)
    assert r.status_code == 200
    assert r.json()["total"] == 2  # só os da bia: nem o caio, nem os próprios
    assert [p["texto"] for p in r.json()["items"]] == ["bia 2"]

    r = client.get("/feed?offset=1&limit=1", headers=ana)
    assert [p["texto"] for p in r.json()["items"]] == ["bia 1"]

    # quem não segue ninguém tem feed vazio; sem login é 401
    assert client.get("/feed", headers=caio).json()["items"] == []
    assert client.get("/feed").status_code == 401


def test_feed_inclui_quem_os_seguidos_seguem(client, logar):
    ana = logar("ana")
    bia = logar("bia")
    caio = logar("caio")  # bia segue o caio; ana não
    davi = logar("davi")  # ninguém na cadeia segue

    client.post("/usuarios/bia/follow", headers=ana)
    client.post("/usuarios/caio/follow", headers=bia)
    client.post("/usuarios/ana/follow", headers=bia)  # volta para a ana: não deve se repetir
    for texto, quem in [("bia", bia), ("caio", caio), ("davi", davi), ("ana", ana)]:
        client.post("/posts", json={"texto": texto}, headers=quem)

    r = client.get("/feed", headers=ana).json()
    assert r["total"] == 2
    assert [p["texto"] for p in r["items"]] == ["caio", "bia"]


def test_post_e_lista_dizem_se_sigo_o_autor(client, logar):
    ana = logar("ana")
    bia = logar("bia")
    client.post("/posts", json={"texto": "x"}, headers=bia)

    assert client.get("/posts", headers=ana).json()["items"][0]["autor_eu_sigo"] is False
    client.post("/usuarios/bia/follow", headers=ana)
    assert client.get("/posts", headers=ana).json()["items"][0]["autor_eu_sigo"] is True
    assert client.get("/usuarios/eu/seguindo", headers=ana).json() == {"usernames": ["bia"]}
