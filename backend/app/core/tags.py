"""Hashtags com índice invertido: tag -> posts que a usam.

Python puro: nenhum import de SQLAlchemy/FastAPI aqui dentro. A API alimenta a
estrutura com ids e textos simples; ela só conhece strings, ints e sets.
"""

import re

# `#tag` com [a-z0-9_]+ depois de casefold; o (?<!\w) evita pegar "a#b" ou entidades "&#39;".
_HASHTAG = re.compile(r"(?<![\w#&])#(\w+)")
_TAG_VALIDA = re.compile(r"[a-z0-9_]+")


def extrair_tags(texto: str) -> list[str]:
    """`#tags` do texto em minúsculas, sem repetir, na ordem em que aparecem."""
    vistas: dict[str, None] = {}
    for bruta in _HASHTAG.findall(texto):
        tag = bruta.casefold()
        if _TAG_VALIDA.fullmatch(tag):  # \w também casa acento; a tag é só ascii
            vistas.setdefault(tag)
    return list(vistas)


def normalizar_tag(tag: str) -> str | None:
    """Tag digitada pelo usuário ("#Fantasia " -> "fantasia"); None se não for válida."""
    tag = tag.strip().lstrip("#").casefold()
    return tag if _TAG_VALIDA.fullmatch(tag) else None


class IndiceTags:
    """dict tag -> set de ids de post (índice invertido) + dict post -> tags.

    - posts de uma tag / contagem: O(1) (lookup em hash)
    - indexar / remover um post: O(t), t = nº de tags do post (poucas)
    - top tags: O(T log T), T = nº de tags distintas
    - reconstruir do zero: O(n) — por isso só acontece no startup
    """

    def __init__(self) -> None:
        self._posts_da_tag: dict[str, set[int]] = {}
        self._tags_do_post: dict[int, frozenset[str]] = {}

    def reconstruir(self, posts: list[tuple[int, list[str]]]) -> None:
        """Chamado no startup com (post_id, tags) de todos os posts do banco."""
        self._posts_da_tag = {}
        self._tags_do_post = {}
        for post_id, tags in posts:
            self.indexar(post_id, tags)

    def indexar(self, post_id: int, tags: list[str]) -> None:
        """Registra (ou substitui, se o post foi editado) as tags de um post."""
        self.remover(post_id)
        unicas = frozenset(tags)
        if not unicas:
            return
        self._tags_do_post[post_id] = unicas
        for tag in unicas:
            self._posts_da_tag.setdefault(tag, set()).add(post_id)

    def remover(self, post_id: int) -> None:
        for tag in self._tags_do_post.pop(post_id, ()):
            ids = self._posts_da_tag[tag]
            ids.discard(post_id)
            if not ids:
                del self._posts_da_tag[tag]

    def ids_da_tag(self, tag: str) -> set[int]:
        return set(self._posts_da_tag.get(tag, ()))

    def ids_com_alguma(self, tags: list[str] | set[str]) -> set[int]:
        """Posts que têm pelo menos uma das tags (união dos conjuntos)."""
        achados: set[int] = set()
        for tag in tags:
            achados |= self._posts_da_tag.get(tag, set())
        return achados

    def mais_usadas(self, limite: int) -> list[tuple[str, int]]:
        """(tag, nº de posts), maior contagem primeiro; empate em ordem alfabética."""
        ranking = sorted(self._posts_da_tag.items(), key=lambda it: (-len(it[1]), it[0]))
        return [(tag, len(ids)) for tag, ids in ranking[:limite]]


# O singleton que a API importa (ver services/tags.py e o lifespan em main.py).
indice_tags = IndiceTags()
