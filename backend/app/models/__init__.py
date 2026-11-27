# 1 arquivo por model — evita conflito de merge quando o time trabalha em paralelo.
from app.models.user import User  # noqa: F401
from app.models.session import Session  # noqa: F401
from app.models.post import Post  # noqa: F401
from app.models.follow import Follow  # noqa: F401
from app.models.like import Like # noqa: F401
from app.models.historia import Historia  # noqa: F401
from app.models.capitulo import Capitulo  # noqa: F401
from app.models.decisao import Decisao  # noqa: F401
from app.models.voto import Voto  # noqa: F401
