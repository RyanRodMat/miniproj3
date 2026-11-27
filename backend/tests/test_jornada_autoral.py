"""Escolha sua jornada: decisões, votos e o mapa da história (issue #11)."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import text


def _iso(**delta) -> str:
    return (datetime.now(timezone.utc) + timedelta(**delta)).isoformat()


def _vencer_prazo(decisao_id: int):
    """Simula a passagem do tempo: empurra o prazo para o passado."""
    from app.db import engine

    passado = (datetime.now(timezone.utc) - timedelta(minutes=1)).replace(tzinfo=None)
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE decisoes SET prazo = :p WHERE id = :i"),
            {"p": passado, "i": decisao_id},
        )


def _artista(client, username="ana"):
    r = client.post(
        "/auth/registro",
        json={"username": username, "name": username, "password": "senha-forte-123", "tipo": "artista"},
    )
    assert r.status_code == 201
    r = client.post("/auth/login", json={"username": username, "password": "senha-forte-123"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _cenario(client, logar, opcoes=("luta", "foge", "negocia")):
    autora = _artista(client)
    hist = client.post("/historias", json={"titulo": "A Torre"}, headers=autora).json()
    cap = client.post(
        f"/historias/{hist['id']}/capitulos", json={"titulo": "Cap 1"}, headers=autora
    ).json()
    r = client.post(
        f"/capitulos/{cap['id']}/decisao",
        json={"pergunta": "O que ela faz?", "opcoes": list(opcoes), "prazo": _iso(hours=1)},
        headers=autora,
    )
    assert r.status_code == 201
    return autora, hist, cap, r.json()


def test_criar_decisao_regras(client, logar):
    autora, hist, cap, decisao = _cenario(client, logar)
    assert decisao["total_votos"] == 0 and decisao["encerrada"] is False
    assert [o["texto"] for o in decisao["opcoes"]] == ["luta", "foge", "negocia"]

    corpo = lambda **kw: {  # noqa: E731
        "pergunta": "?", "opcoes": ["a", "b"], "prazo": _iso(hours=1), **kw
    }
    # já tem decisão → 409
    assert client.post(f"/capitulos/{cap['id']}/decisao", json=corpo(), headers=autora).status_code == 409
    # outro usuário → 403; capítulo inexistente → 404; sem login → 401
    leitor = logar("leitor")
    assert client.post(f"/capitulos/{cap['id']}/decisao", json=corpo(), headers=leitor).status_code == 403
    assert client.post("/capitulos/999/decisao", json=corpo(), headers=autora).status_code == 404
    assert client.post(f"/capitulos/{cap['id']}/decisao", json=corpo()).status_code == 401


def test_decisao_valida_opcoes_e_prazo(client, logar):
    autora = _artista(client)
    hist = client.post("/historias", json={"titulo": "H"}, headers=autora).json()
    cap = client.post(f"/historias/{hist['id']}/capitulos", json={"titulo": "1"}, headers=autora).json()
    url = f"/capitulos/{cap['id']}/decisao"
    base = {"pergunta": "?", "prazo": _iso(hours=1)}

    assert client.post(url, json={**base, "opcoes": ["so uma"]}, headers=autora).status_code == 422
    assert client.post(url, json={**base, "opcoes": list("abcde")}, headers=autora).status_code == 422
    assert client.post(url, json={**base, "opcoes": ["a", " "]}, headers=autora).status_code == 422
    passado = {"pergunta": "?", "opcoes": ["a", "b"], "prazo": _iso(hours=-1)}
    assert client.post(url, json=passado, headers=autora).status_code == 422
    # 2 e 4 opções valem
    ok = client.post(url, json={**base, "opcoes": list("abcd")}, headers=autora)
    assert ok.status_code == 201


def test_votar_e_ler_resultado(client, logar):
    autora, _, _, decisao = _cenario(client, logar)
    bia, caio = logar("bia"), logar("caio")
    url = f"/decisoes/{decisao['id']}"

    r = client.post(f"{url}/votar", json={"opcao": 1}, headers=bia)
    assert r.status_code == 200
    assert r.json()["ja_votei"] is True and r.json()["minha_opcao"] == 1
    client.post(f"{url}/votar", json={"opcao": 1}, headers=caio)

    corpo = client.get(url, headers=bia).json()
    assert [o["votos"] for o in corpo["opcoes"]] == [0, 2, 0]
    assert corpo["total_votos"] == 2 and corpo["encerrada"] is False
    # quem não votou vê ja_votei = false
    assert client.get(url, headers=autora).json()["ja_votei"] is False


def test_segundo_voto_indice_invalido_e_sem_login(client, logar):
    _, _, _, decisao = _cenario(client, logar)
    bia = logar("bia")
    url = f"/decisoes/{decisao['id']}/votar"

    assert client.post(url, json={"opcao": 0}, headers=bia).status_code == 200
    assert client.post(url, json={"opcao": 2}, headers=bia).status_code == 409  # segundo voto
    assert client.post(url, json={"opcao": 3}, headers=logar("caio")).status_code == 422
    assert client.post(url, json={"opcao": -1}, headers=logar("dani")).status_code == 422
    assert client.post(url, json={"opcao": 0}).status_code == 401
    assert client.post("/decisoes/999/votar", json={"opcao": 0}, headers=bia).status_code == 404
    assert client.get("/decisoes/999", headers=bia).status_code == 404


def test_votar_depois_do_prazo_e_409_e_resultado_fecha(client, logar):
    _, _, _, decisao = _cenario(client, logar)
    bia = logar("bia")
    client.post(f"/decisoes/{decisao['id']}/votar", json={"opcao": 2}, headers=bia)

    _vencer_prazo(decisao["id"])
    r = client.post(f"/decisoes/{decisao['id']}/votar", json={"opcao": 0}, headers=logar("caio"))
    assert r.status_code == 409

    corpo = client.get(f"/decisoes/{decisao['id']}", headers=bia).json()
    assert corpo["encerrada"] is True and corpo["vencedora"] == 2


def test_proximo_capitulo_nasce_da_opcao_vencedora(client, logar):
    autora, hist, cap, decisao = _cenario(client, logar)
    bia, caio, dani = logar("bia"), logar("caio"), logar("dani")
    url_cap = f"/historias/{hist['id']}/capitulos"
    nasce = lambda opcao: client.post(  # noqa: E731
        url_cap,
        json={"titulo": "Cap 2", "pai_id": cap["id"], "opcao_origem": opcao},
        headers=autora,
    )

    # votação aberta → 409
    assert nasce(1).status_code == 409

    client.post(f"/decisoes/{decisao['id']}/votar", json={"opcao": 1}, headers=bia)
    client.post(f"/decisoes/{decisao['id']}/votar", json={"opcao": 1}, headers=caio)
    client.post(f"/decisoes/{decisao['id']}/votar", json={"opcao": 0}, headers=dani)
    _vencer_prazo(decisao["id"])

    assert nasce(0).status_code == 409  # não foi a vencedora
    r = nasce(1)
    assert r.status_code == 201
    assert r.json()["numero"] == 2 and r.json()["opcao_origem"] == 1
    assert nasce(1).status_code == 409  # a opção já tem capítulo


def test_mapa_da_jornada_marca_o_caminho_e_as_opcoes_nao_escolhidas(client, logar):
    autora, hist, cap, decisao = _cenario(client, logar)
    bia, caio = logar("bia"), logar("caio")
    client.post(f"/decisoes/{decisao['id']}/votar", json={"opcao": 2}, headers=bia)
    client.post(f"/decisoes/{decisao['id']}/votar", json={"opcao": 2}, headers=caio)

    url = f"/historias/{hist['id']}/jornada"
    aberta = client.get(url, headers=bia).json()
    assert [p["capitulo_id"] for p in aberta["caminho"]] == [cap["id"]]
    assert not any(o["escolhida"] for o in aberta["caminho"][0]["decisao"]["opcoes"])

    _vencer_prazo(decisao["id"])
    client.post(
        f"/historias/{hist['id']}/capitulos",
        json={"titulo": "Cap 2", "pai_id": cap["id"], "opcao_origem": 2},
        headers=autora,
    )
    mapa = client.get(url, headers=bia).json()
    assert mapa["titulo"] == "A Torre"
    assert [p["numero"] for p in mapa["caminho"]] == [1, 2]
    opcoes = mapa["caminho"][0]["decisao"]["opcoes"]
    assert [o["escolhida"] for o in opcoes] == [False, False, True]
    assert opcoes[2]["votos"] == 2
    assert mapa["caminho"][1]["decisao"] is None
    assert client.get("/historias/999/jornada", headers=bia).status_code == 404


def test_jornada_sobrevive_a_restart(client, logar):
    """O lifespan reconstrói a árvore a partir do banco."""
    from app.core.jornada import jornada
    from app.db import SessionLocal
    from app.services.decisoes import reconstruir_jornada

    autora, hist, cap, decisao = _cenario(client, logar)
    client.post(f"/decisoes/{decisao['id']}/votar", json={"opcao": 1}, headers=logar("bia"))
    _vencer_prazo(decisao["id"])
    client.post(
        f"/historias/{hist['id']}/capitulos",
        json={"titulo": "Cap 2", "pai_id": cap["id"], "opcao_origem": 1},
        headers=autora,
    )

    jornada.reconstruir([], [])  # simula o processo reiniciando com memória zerada
    with SessionLocal() as db:
        reconstruir_jornada(db)

    mapa = client.get(f"/historias/{hist['id']}/jornada", headers=autora).json()
    assert [p["numero"] for p in mapa["caminho"]] == [1, 2]
