"""Upload de imagem em posts (issue #9)."""
import pytest

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100


@pytest.fixture(autouse=True)
def _pasta_temporaria(tmp_path, monkeypatch):
    # ajuste o caminho se o UPLOAD_DIR morar em outro módulo
    monkeypatch.setattr("app.services.uploads.UPLOAD_DIR", tmp_path)


def _artista(client, username):
    r = client.post(
        "/auth/registro",
        json={"username": username, "name": "A", "password": "senha-forte-123", "tipo": "artista"},
    )
    assert r.status_code == 201
    r = client.post("/auth/login", json={"username": username, "password": "senha-forte-123"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _post(client, autor):
    r = client.post("/posts", json={"texto": "minha arte"}, headers=autor)
    assert r.status_code == 201
    return r.json()["id"]


def _arquivo(conteudo=PNG, nome="a.png", tipo="image/png"):
    return {"arquivo": (nome, conteudo, tipo)}


def test_autor_envia_imagem(client, tmp_path):
    ana = _artista(client, "ana")
    pid = _post(client, ana)

    r = client.post(f"/posts/{pid}/imagem", files=_arquivo(), headers=ana)
    assert r.status_code == 200
    url = r.json()["imagem_url"]
    assert url.startswith("/uploads/") and url.endswith(".png")
    assert "a.png" not in url                      # nome gerado com uuid
    assert (tmp_path / url.rsplit("/", 1)[1]).exists()


def test_outro_usuario_recebe_403(client, logar, tmp_path):
    ana = _artista(client, "ana")
    bia = logar("bia")
    pid = _post(client, ana)

    r = client.post(f"/posts/{pid}/imagem", files=_arquivo(), headers=bia)
    assert r.status_code == 403
    assert list(tmp_path.iterdir()) == []          # nada foi gravado


def test_imagem_maior_que_2mb_recebe_413(client):
    ana = _artista(client, "ana")
    pid = _post(client, ana)
    grande = b"\x89PNG\r\n\x1a\n" + b"0" * (2 * 1024 * 1024)

    r = client.post(f"/posts/{pid}/imagem", files=_arquivo(grande), headers=ana)
    assert r.status_code == 413


def test_tipo_invalido_e_recusado(client):
    ana = _artista(client, "ana")
    pid = _post(client, ana)

    r = client.post(f"/posts/{pid}/imagem", files=_arquivo(b"texto", "a.txt", "text/plain"), headers=ana)
    assert r.status_code == 415                    # ajuste se o seu service usa outro código

    # content-type mentiroso: diz png, mas os bytes não são
    r = client.post(f"/posts/{pid}/imagem", files=_arquivo(b"isso nao e png"), headers=ana)
    assert r.status_code == 415


def test_post_inexistente_e_sem_login(client):
    ana = _artista(client, "ana")
    assert client.post("/posts/99999/imagem", files=_arquivo(), headers=ana).status_code == 404
    assert client.post("/posts/1/imagem", files=_arquivo()).status_code == 401

def test_endpoint_generico_de_imagem(client, tmp_path):
    ana = _artista(client, "ana")
    r = client.post("/imagens", files=_arquivo(), headers=ana)
    assert r.status_code == 200
    assert r.json()["imagem_url"].startswith("/uploads/")
    assert client.post("/imagens", files=_arquivo()).status_code == 401