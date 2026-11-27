import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

# ancorada no pacote do backend: não depende de onde o uvicorn foi iniciado
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
URL_PREFIXO = "/uploads/"
MAX_BYTES = 2 * 1024 * 1024
TIPOS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def _assinatura_valida(dados: bytes, ext: str) -> bool:
    if ext == ".jpg":
        return dados.startswith(b"\xff\xd8\xff")
    if ext == ".png":
        return dados.startswith(b"\x89PNG\r\n\x1a\n")
    if ext == ".webp":
        return dados[:4] == b"RIFF" and dados[8:12] == b"WEBP"
    return False


async def salvar_imagem(arquivo: UploadFile) -> str:
    ext = TIPOS.get(arquivo.content_type)
    if not ext:
        raise HTTPException(415, "Use jpg, png ou webp")
    dados = await arquivo.read(MAX_BYTES + 1)  # lê no máximo 2 MB + 1 byte
    if len(dados) > MAX_BYTES:
        raise HTTPException(413, "Imagem maior que 2 MB")
    if not _assinatura_valida(dados, ext):
        raise HTTPException(415, "Arquivo não é uma imagem válida")
    UPLOAD_DIR.mkdir(exist_ok=True)
    nome = f"{uuid.uuid4().hex}{ext}"
    (UPLOAD_DIR / nome).write_bytes(dados)
    return f"{URL_PREFIXO}{nome}"


def apagar_imagem(url: str | None) -> None:
    """Remove do disco um arquivo enviado por upload; ignora URLs externas ou de /seed/."""
    if url and url.startswith(URL_PREFIXO):
        (UPLOAD_DIR / Path(url).name).unlink(missing_ok=True)
