"""Seed de dados fake: uma rede de quadrinistas e ilustradores iniciantes.

`seed_fake(db)` popula usuários (artistas e leitores), posts de texto e de arte,
follows, curtidas, tags de interesse e duas histórias interativas com decisões
votadas e uma decisão em aberto. É determinístico (mesma semente, mesma rede) e
idempotente (se a rede do seed já existe, não faz nada).

As imagens dos posts são arquivos versionados em frontend/public/seed/ (gerados
por scripts/gerar_imagens_seed.py), servidos pelo front em /seed/<nome>.svg.
Eles não dependem do `uploads/`, que some no deploy.

Todos os usuários do seed entram com a senha SENHA_SEED. Rode com: make seed
"""

import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Base, SessionLocal, engine
from app.models.decisao import Decisao, Opcao, Voto
from app.models.follow import Follow
from app.models.historia import Capitulo, Historia
from app.models.interesse import Interesse
from app.models.like import Like
from app.models.post import Post
from app.models.user import User

SENHA_SEED = "quadrinhos-123"
SEMENTE = 2026

# ---------- usuários: (username, nome, bio, tipo, tags de interesse) ----------

ARTISTAS = [
    ("mari_nanquim", "Mariana Nanquim", "Desenho dragões e torres tortas desde os 12. Autora de A Torre do Último Farol.", ["fantasia", "aventura"]),
    ("bruno_tracos", "Bruno Traços", "Mapas, criaturas e muito lápis 2B. Aprendendo a colorir digital.", ["fantasia", "aventura"]),
    ("lia_sombras", "Lia Sombras", "Quadrinhos de terror em preto e branco. Meu café é sempre sem açúcar.", ["terror"]),
    ("caio_pesadelo", "Caio Pesadelo", "Ilustrador iniciante, fã de casa mal-assombrada e hachura pesada.", ["terror", "scifi"]),
    ("duda_cafe", "Duda Cafezinho", "Tirinhas do cotidiano: café, gato e prazo estourado.", ["slice_of_life", "humor"]),
    ("nina_quadrinhos", "Nina Quadrinhos", "Faço HQ curtinha sobre morar sozinha pela primeira vez.", ["slice_of_life", "humor"]),
    ("theo_orbita", "Theo Órbita", "Roteirista e desenhista de ficção científica. Plantão 3 da Estação Órion é meu primeiro webcomic.", ["scifi", "aventura"]),
    ("vini_pixel", "Vini Pixel", "Pixel art e robôs. Estudando perspectiva na marra.", ["scifi", "aventura"]),
    ("bia_aquarela", "Bia Aquarela", "Aquarela, fantasia leve e cenas de dia de chuva.", ["fantasia", "slice_of_life"]),
    ("rafa_tinta", "Rafa Tinta", "Nanquim e monstros do espaço. Primeira HQ autoral saindo do forno.", ["terror", "scifi"]),
    ("jess_zine", "Jess Zine", "Faço zines xerocadas sobre amizade e cidade pequena.", ["slice_of_life"]),
    ("otto_roteiro", "Otto Roteiro", "Escrevo roteiros e procuro desenhista. Fantasia com viagem no tempo.", ["scifi", "fantasia"]),
]

LEITORES = [
    ("leo_leitor", "Leonardo Páginas", "Leio tudo que tem dragão. Comento mais do que deveria.", ["fantasia", "aventura"]),
    ("carol_le", "Carol Lê", "Terror é meu gênero de conforto. Não me chamem depois das 22h.", ["terror"]),
    ("pedro_manga", "Pedro Mangá", "Colecionador de tankobon e de tirinha engraçada.", ["slice_of_life", "humor"]),
    ("alice_nerd", "Alice Nerd", "Ficção científica e fantasia, nessa ordem. Maratonista de webcomic.", ["scifi", "fantasia"]),
    ("gui_hq", "Gui HQ", "Gibiteca ambulante. Dou feedback honesto (e gentil).", ["terror", "scifi"]),
    ("sofia_zine", "Sofia Zine", "Apaixonada por zine e por quadrinho de gente comum.", ["slice_of_life"]),
    ("tati_le", "Tati Contos", "Leitora de fantasia, aspirante a roteirista.", ["fantasia"]),
    ("davi_roda", "Davi Roda", "Acompanho toda história interativa e voto sempre na opção errada.", ["scifi", "humor"]),
    ("ju_pagina", "Ju Página", "Terror e slice of life: ou me assusto ou me emociono.", ["terror", "slice_of_life"]),
    ("marcos_vol1", "Marcos Volume 1", "Sempre começo pelo volume 1. Fã de aventura.", ["aventura", "fantasia"]),
]

# imagens por gênero principal (arquivos em frontend/public/seed/)
IMAGENS = {
    "fantasia": ["fantasia-torre", "fantasia-dragao", "fantasia-floresta"],
    "terror": ["terror-casa", "terror-olhos", "terror-corredor"],
    "slice_of_life": ["sol-cafe", "sol-janela", "sol-onibus"],
    "scifi": ["scifi-estacao", "scifi-planeta", "scifi-robo"],
}

# ---------- posts de arte: (autor, texto); a imagem vem do gênero do autor ----------

POSTS_ARTE = [
    ("mari_nanquim", "Rascunho do farol do capítulo 3. A luz vai ser o único colorido da página. #fantasia"),
    ("mari_nanquim", "Finalizei a arte final do guardião de sal. Demorei três noites só na textura. #fantasia #aventura"),
    ("mari_nanquim", "Estudo de atmosfera: o céu antes da tempestade na Torre. Feedback de cor é bem-vindo! #fantasia"),
    ("bruno_tracos", "Mapa do reino de Valdar, versão 2. Agora com rios que fazem sentido. #fantasia #aventura"),
    ("bruno_tracos", "Primeira tentativa de dragão colorido no tablet. Sim, ele está meio verde demais. #fantasia"),
    ("bruno_tracos", "Floresta encantada em lápis e um pouco de luz digital. #fantasia"),
    ("lia_sombras", "Página 4 do conto 'A casa do fim da rua'. Só nanquim e muita paciência. #terror"),
    ("lia_sombras", "Teste de enquadramento: o corredor que nunca acaba. Está assustador ou só confuso? #terror"),
    ("lia_sombras", "Pesadelo da semana virou ilustração. Dormi mal, desenhei bem. #terror"),
    ("caio_pesadelo", "Casa mal-assombrada, versão noturna. Treinando luz e sombra. #terror"),
    ("caio_pesadelo", "Todos os olhos olhando de volta. Experimento de composição. #terror #scifi"),
    ("caio_pesadelo", "Corredor do hospital abandonado. Referência: meu antigo colégio. #terror"),
    ("duda_cafe", "Tirinha de hoje: o café esfriou de novo enquanto eu desenhava. #slice_of_life #humor"),
    ("duda_cafe", "Cantinho da janela onde eu desenho. O gato aprovou a composição. #slice_of_life"),
    ("duda_cafe", "Voltando do estágio no ônibus lotado, virou página de caderno. #slice_of_life"),
    ("nina_quadrinhos", "Capítulo 1 de 'Morando sozinha': primeiro dia sem ninguém para lavar a louça. #slice_of_life #humor"),
    ("nina_quadrinhos", "Rascunho da cena do café da manhã. Quero que dê vontade de abraçar a personagem. #slice_of_life"),
    ("nina_quadrinhos", "Ônibus das 7h, a eterna inspiração. #slice_of_life #humor"),
    ("theo_orbita", "Capa da Estação Órion, versão 3. Troquei o azul por algo mais frio. #scifi"),
    ("theo_orbita", "Planeta onde o Plantão 3 vai pousar no capítulo 2. #scifi #aventura"),
    ("theo_orbita", "Design do robô de manutenção. Ele é meio fofo, mas guarda um segredo. #scifi"),
    ("vini_pixel", "Robô novo em pixel art 64x64. A antena foi a parte mais difícil. #scifi"),
    ("vini_pixel", "Estação espacial em pixel art, estudando paleta limitada. #scifi #aventura"),
    ("vini_pixel", "Planeta vermelho, primeira cena do meu jogo-quadrinho. #scifi"),
    ("bia_aquarela", "Aquarela: torre ao pôr do sol, deixei o papel molhado demais e amei o erro. #fantasia"),
    ("bia_aquarela", "Café da tarde na chuva, aquarela rápida. #slice_of_life"),
    ("bia_aquarela", "Floresta com vaga-lumes, em aquarela e guache. #fantasia"),
    ("rafa_tinta", "Monstro do espaço profundo, nanquim sobre papel. #scifi #terror"),
    ("rafa_tinta", "Cena de abertura da minha HQ: a casa que ninguém quer visitar. #terror"),
    ("jess_zine", "Página da zine 'Cidade pequena': a janela da casa da vovó. #slice_of_life"),
    ("jess_zine", "Ilustração da capa da zine, café com pão de queijo. #slice_of_life"),
    ("otto_roteiro", "Concept do robô do meu roteiro. Alguém quer desenhar a HQ comigo? #scifi #fantasia"),
]

# ---------- posts de texto: discussões, bastidores e pedidos de feedback ----------

POSTS_TEXTO = [
    ("mari_nanquim", "Bastidores: o capítulo 3 da Torre quase não saiu. Reescrevi o final quatro vezes até a decisão ficar justa para os dois lados. #fantasia"),
    ("mari_nanquim", "Pergunta para quem lê histórias interativas: vocês preferem decisões com resultado imediato ou que só mostram o efeito dois capítulos depois? #fantasia"),
    ("bruno_tracos", "Dica de iniciante: faça o mapa ANTES do roteiro. Metade dos meus problemas de continuidade sumiu. #fantasia #aventura"),
    ("bruno_tracos", "Alguém conhece bons pincéis grátis para o tablet? Meu traço está duro demais. #fantasia"),
    ("lia_sombras", "Terror funciona no que você NÃO mostra. Hoje cortei três painéis só para o susto vir da página seguinte. #terror"),
    ("lia_sombras", "Peço feedback: o diálogo do capítulo 2 está expositivo demais? Quero que pareça conversa de verdade. #terror"),
    ("caio_pesadelo", "Hachura ou retícula para clima de terror? Estou dividido e minhas páginas estão sofrendo. #terror"),
    ("caio_pesadelo", "Fiz meu primeiro painel de página dupla. Meu scanner agora me odeia. #terror #scifi"),
    ("duda_cafe", "Meta da semana: uma tirinha por dia. Dia 1: feito. Dia 2: o gato dormiu no tablet. #slice_of_life #humor"),
    ("duda_cafe", "Vocês acham que tirinha de quatro quadros ainda funciona hoje ou só em vertical? #slice_of_life"),
    ("nina_quadrinhos", "Hoje percebi que a HQ sobre morar sozinha é mais sobre solidão boa do que sobre louça suja. Vou ajustar o tom. #slice_of_life"),
    ("nina_quadrinhos", "Pedido de feedback: o balão da página 3 está cobrindo a expressão da personagem? #slice_of_life #humor"),
    ("theo_orbita", "Bastidores do Plantão 3: planejei 12 capítulos, mas a comunidade vai decidir o rumo de pelo menos metade. Assustador e empolgante. #scifi"),
    ("theo_orbita", "Quem vota na decisão aberta da Estação Órion? Prometo não alterar o resultado depois. #scifi"),
    ("vini_pixel", "Pixel art é mais sobre o que você tira do que o que você coloca. Frase minha, acabei de inventar. #scifi"),
    ("vini_pixel", "Estudando perspectiva há duas semanas e ainda desenho cubos tortos. Seguimos. #scifi #aventura"),
    ("bia_aquarela", "Aquarela não perdoa: errou, o papel guarda. Mas é por isso que eu amo. #fantasia #slice_of_life"),
    ("rafa_tinta", "Terminei o roteiro da minha primeira HQ autoral! Agora começa a parte difícil: desenhar tudo. #terror #scifi"),
    ("jess_zine", "Imprimi a primeira tiragem da zine: 30 cópias, 29 vão para amigos. #slice_of_life"),
    ("otto_roteiro", "Procuro desenhista iniciante para uma HQ de fantasia com viagem no tempo. Aceito portfólio pequeno, importa a vontade. #fantasia #scifi"),
    ("leo_leitor", "Terminei de ler A Torre do Último Farol até onde saiu. Quero saber o que acontece no próximo capítulo e já votei! #fantasia"),
    ("leo_leitor", "Recomendação de dragão bonito: o do Bruno Traços. Cor verde demais, mas é charme. #fantasia"),
    ("carol_le", "Li a página dupla do Caio com a luz apagada. Má ideia, ótimo quadrinho. #terror"),
    ("carol_le", "Indicações de terror curto para ler antes de dormir (ou não)? #terror"),
    ("pedro_manga", "As tirinhas da Duda me acompanham no ônibus todo dia. Obrigado por existirem. #slice_of_life #humor"),
    ("alice_nerd", "Discussão: em ficção científica, vale mais o mistério ou a ciência? Eu fico com o mistério. #scifi"),
    ("gui_hq", "Dei feedback em cinco páginas hoje. Dica: comece pelo que funciona, depois fale do resto. #terror #scifi"),
    ("sofia_zine", "Comprei a zine da Jess e li de uma vez. Quero uma continuação! #slice_of_life"),
    ("tati_le", "Estou tentando escrever meu primeiro roteiro de fantasia. Quem tem dicas de construção de mundo? #fantasia"),
    ("davi_roda", "Votei no fim da Estação Órion e perdi de novo. Já virou tradição. #scifi #humor"),
    ("ju_pagina", "Terror e slice of life têm algo em comum: o detalhe pequeno é o que fica. #terror #slice_of_life"),
    ("marcos_vol1", "Comecei a ler a Torre do Último Farol pelo capítulo 1, claro. Que atmosfera! #fantasia #aventura"),
]

# ---------- histórias interativas ----------

HISTORIAS = [
    {
        "autor": "mari_nanquim",
        "titulo": "A Torre do Último Farol",
        "sinopse": "Mira volta à vila costeira para descobrir por que o farol, que nunca falhou, apagou numa noite sem vento.",
        "tag": "fantasia",
        "capitulos": [
            {
                "titulo": "A luz que se apagou",
                "texto": "Faz três noites que o mar não tem guia. Mira chega à base da torre quando o vento muda de direção. A porta está entreaberta, e lá no alto, algo respira.",
                "imagem": "fantasia-torre",
                "decisao": ("Mira entra pela porta ou escala o penhasco?", ["Entrar pela porta, com cuidado", "Escalar o penhasco e entrar pela janela"], False),
            },
            {
                "titulo": "O guardião de sal",
                "texto": "Dentro da torre, uma figura de sal bloqueia a escada. Ele fala com a voz de quem nunca dormiu: 'Só passa quem me disser o próprio nome'.",
                "imagem": "fantasia-dragao",
                "decisao": ("O guardião pede o nome verdadeiro. O que Mira faz?", ["Diz o nome verdadeiro", "Inventa um nome falso"], False),
            },
            {
                "titulo": "O andar de cima",
                "texto": "No topo, a lanterna está intacta e apagada. Uma voz sussurra que ela só acende com uma oferta. Lá fora, um navio ainda procura a costa.",
                "imagem": "fantasia-floresta",
                "decisao": ("O que Mira oferece à lanterna?", ["Sua memória mais feliz", "A chave da torre", "Nada: tenta acender sozinha"], True),
            },
        ],
    },
    {
        "autor": "theo_orbita",
        "titulo": "Plantão 3 da Estação Órion",
        "sinopse": "Na estação de manutenção mais isolada do setor, a técnica Ione recebe um sinal que não deveria existir.",
        "tag": "scifi",
        "capitulos": [
            {
                "titulo": "Sinal fantasma",
                "texto": "O alarme do plantão da madrugada toca duas vezes e para. No painel, uma frequência que ninguém usa há trinta anos pisca em azul.",
                "imagem": "scifi-estacao",
                "decisao": ("Ione investiga o sinal agora ou avisa a base primeiro?", ["Investigar sozinha", "Avisar a base antes"], False),
            },
            {
                "titulo": "O robô que não estava no inventário",
                "texto": "No hangar 7, um robô de manutenção antigo olha para Ione. O registro da estação diz que ele foi desmontado há décadas.",
                "imagem": "scifi-robo",
                "decisao": ("O robô oferece uma troca: um segredo por acesso ao núcleo. Ione...", ["Aceita a troca", "Recusa e tranca o hangar", "Tenta desligá-lo"], True),
            },
        ],
    },
]


def _hash_senha() -> str:
    # mesma senha para todos → 1 bcrypt só (hashear 22 vezes demora vários segundos)
    return bcrypt.hashpw(SENHA_SEED.encode(), bcrypt.gensalt()).decode()


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _genero_do_post(texto: str, padrao: str) -> str:
    """Gênero da arte = primeira hashtag do texto que tem imagem; senão, o do autor."""
    for palavra in texto.split():
        if palavra.startswith("#") and palavra[1:] in IMAGENS:
            return palavra[1:]
    return padrao


def seed_fake(db: Session) -> dict[str, int]:
    """Popula a rede fake. Devolve as contagens criadas (vazio se já tinha seed)."""
    Base.metadata.create_all(engine)
    if db.scalar(select(User).where(User.username == ARTISTAS[0][0])):
        return {}

    rng = random.Random(SEMENTE)
    agora = _agora()
    senha_hash = _hash_senha()

    # --- usuários + tags de interesse ---
    usuarios: dict[str, User] = {}
    tags: dict[str, list[str]] = {}
    for tipo, lista in (("artista", ARTISTAS), ("leitor", LEITORES)):
        for username, nome, bio, interesses in lista:
            usuarios[username] = User(
                username=username,
                name=nome,
                bio=bio,
                tipo=tipo,
                password_hash=senha_hash,
                created_at=agora - timedelta(days=rng.randint(20, 40)),
            )
            tags[username] = interesses
    db.add_all(usuarios.values())
    db.flush()  # preenche os ids
    db.add_all(
        Interesse(user_id=usuarios[u].id, tag=t) for u, ts in tags.items() for t in ts
    )

    # --- posts: texto + arte, embaralhados e espalhados pelos últimos 14 dias ---
    contador_imagem: dict[str, int] = {}
    pendentes: list[tuple[str, str, str | None]] = []
    for autor, texto in POSTS_TEXTO:
        pendentes.append((autor, texto, None))
    for autor, texto in POSTS_ARTE:
        genero = _genero_do_post(texto, tags[autor][0])
        n = contador_imagem.get(genero, 0)
        contador_imagem[genero] = n + 1
        arquivo = IMAGENS[genero][n % len(IMAGENS[genero])]
        pendentes.append((autor, texto, f"/seed/{arquivo}.svg"))
    rng.shuffle(pendentes)

    posts: list[Post] = []
    inicio = agora - timedelta(days=14)
    passo = timedelta(days=14) / len(pendentes)
    for i, (autor, texto, imagem) in enumerate(pendentes):
        posts.append(
            Post(
                autor_id=usuarios[autor].id,
                texto=texto,
                imagem_url=imagem,
                created_at=inicio + passo * i + timedelta(minutes=rng.randint(0, 30)),
            )
        )
    db.add_all(posts)
    db.flush()

    # --- follows: quem tem tag em comum (leitor → artista; artista → artista) ---
    pares: set[tuple[str, str]] = set()
    nomes_artistas = [a[0] for a in ARTISTAS]
    leitores = {l[0] for l in LEITORES}
    for seguidor in usuarios:
        candidatos = [
            a for a in nomes_artistas
            if a != seguidor and set(tags[a]) & set(tags[seguidor])
        ]
        rng.shuffle(candidatos)
        limite = 4 if seguidor in leitores else 2
        for alvo in candidatos[:limite]:
            pares.add((seguidor, alvo))
    db.add_all(
        Follow(follower_id=usuarios[a].id, followed_id=usuarios[b].id)
        for a, b in sorted(pares)
    )

    # --- curtidas: mais nos posts de quem se segue, algumas em tags em comum ---
    seguidos_de: dict[int, set[int]] = {}
    for a, b in pares:
        seguidos_de.setdefault(usuarios[a].id, set()).add(usuarios[b].id)
    curtidas: set[tuple[int, int]] = set()
    for u in usuarios.values():
        for p in posts:
            if p.autor_id == u.id:
                continue
            chance = 0.35 if p.autor_id in seguidos_de.get(u.id, set()) else 0.03
            if rng.random() < chance:
                curtidas.add((u.id, p.id))
    db.add_all(
        Like(liker_id=u, liked_post_id=p, created_at=agora - timedelta(hours=rng.randint(1, 300)))
        for u, p in sorted(curtidas)
    )

    # --- histórias interativas ---
    n_decisoes = n_votos = 0
    todos = list(usuarios.values())
    for h in HISTORIAS:
        historia = Historia(
            autor_id=usuarios[h["autor"]].id,
            titulo=h["titulo"],
            sinopse=h["sinopse"],
            tag=h["tag"],
            created_at=agora - timedelta(days=12),
        )
        db.add(historia)
        db.flush()
        for ordem, cap in enumerate(h["capitulos"], start=1):
            capitulo = Capitulo(
                historia_id=historia.id,
                ordem=ordem,
                titulo=cap["titulo"],
                texto=cap["texto"],
                imagem_url=f"/seed/{cap['imagem']}.svg",
            )
            db.add(capitulo)
            db.flush()
            pergunta, textos, aberta = cap["decisao"]
            decisao = Decisao(capitulo_id=capitulo.id, pergunta=pergunta, aberta=aberta)
            db.add(decisao)
            db.flush()
            opcoes = [Opcao(decisao_id=decisao.id, texto=t) for t in textos]
            db.add_all(opcoes)
            db.flush()
            n_decisoes += 1
            # leitores votam em todas; só quem não é o autor da história
            for u in todos:
                if u.id == historia.autor_id or rng.random() < 0.25:
                    continue
                db.add(Voto(user_id=u.id, decisao_id=decisao.id, opcao_id=rng.choice(opcoes).id))
                n_votos += 1

    db.commit()
    return {
        "usuarios": len(usuarios),
        "posts": len(posts),
        "follows": len(pares),
        "curtidas": len(curtidas),
        "historias": len(HISTORIAS),
        "decisoes": n_decisoes,
        "votos": n_votos,
    }


def main() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        contagens = seed_fake(db)
    if not contagens:
        print("banco já tem o seed — nada a fazer")
        return
    resumo = ", ".join(f"{v} {k}" for k, v in contagens.items())
    print(f"seed ok: {resumo}")
    print(f"senha de todos os usuários: {SENHA_SEED}")


if __name__ == "__main__":
    main()
