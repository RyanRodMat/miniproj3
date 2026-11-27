from fastapi import APIRouter, Depends, File, UploadFile

from app.deps import get_current_user      # use o import real do seu projeto
from app.models.user import User
from app.services.uploads import salvar_imagem

router = APIRouter(prefix="/imagens", tags=["imagens"])


@router.post("")
async def enviar_imagem(
    arquivo: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    return {"imagem_url": await salvar_imagem(arquivo)}