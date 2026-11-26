# 1 arquivo por model — evita conflito de merge quando o time trabalha em paralelo.
from app.models.user import User  # noqa: F401
from app.models.session import Session  # noqa: F401
from app.models.post import Post  # noqa: F401
from app.models.follow import Follow  # noqa: F401
from app.models.like import Like # noqa: F401
from app.models.interesse import Interesse  # noqa: F401
from app.models.historia import Capitulo, Historia  # noqa: F401
from app.models.decisao import Decisao, Opcao, Voto  # noqa: F401
