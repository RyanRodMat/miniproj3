# Decisões do time

**Time:** 
Maria Laura (@mlaurasarmentov)
Matheus Brito (@matheuscbrito)
Ryan Rodrigues (@RyanRodMat)

Este arquivo acompanha o projeto. Comecem com o que já sabem e atualizem quando
as decisões mudarem.

## Produto

**Marte** é uma rede social de quadrinhos e ilustração independente.

- **Público:** quadrinistas e ilustradores iniciantes (quem desenha e ainda não
  tem público) e os leitores que acompanham webcomics e gostam de dar feedback.
- **Problema:** hoje o artista iniciante posta em redes feitas para fotos e
  vídeos curtos, onde a arte some no meio do feed, o leitor não tem como
  influenciar a história e quem tem poucos seguidores nunca aparece.
- **Como a rede resolve:** o artista publica arte, tirinhas e capítulos num feed
  de texto e imagem; o leitor decide o rumo da história por votação; e o Em alta
  premia quem engaja agora, não quem já é famoso.
- **Como saberíamos que funcionou:** o leitor volta no dia seguinte para ver o
  resultado da votação e o capítulo novo; e um artista com poucos seguidores
  aparece no Em alta por causa de um post.

## Decisões de produto

### 1. Escolha sua jornada em vez de só "publicar capítulo"

- **Contexto:** webcomic comum é leitura passiva; o diferencial que a rede
  podia ter era o leitor mexer na história.
- **Opções:** só comentários nos capítulos, enquetes soltas, ou votação
  amarrada ao capítulo seguinte.
- **Escolha:** cada capítulo termina numa decisão do personagem (2 a 4 opções,
  com prazo). O capítulo seguinte só nasce da opção vencedora, e o mapa da
  história mostra o caminho tomado e "o que poderia ter sido".
- **O que cortamos e por quê:** votação aberta a qualquer momento e capítulos
  paralelos para todas as opções. Um caminho só mantém a história coerente e o
  trabalho do artista viável (ele desenha um capítulo por rodada).

### 2. Feed misto de texto e arte

- **Contexto:** artista também conversa (bastidores, pedido de feedback), e a
  arte sozinha não cria vínculo.
- **Opções:** feed só de imagens ou feed misto, como no Twitter.
- **Escolha:** o post é texto, com `imagem_url` opcional. O feed mistura quem o
  usuário segue e quem os seguidos seguem, mais novo primeiro.
- **O que cortamos e por quê:** galeria só de imagens e filtro "só arte".
  Separar os dois afastaria justamente a conversa que faz o leitor voltar.

### 3. Em alta por engajamento recente

- **Contexto:** num feed cronológico, o iniciante só é visto por quem já o segue.
- **Opções:** ranking por total de curtidas (premia o famoso) ou por engajamento
  com queda no tempo.
- **Escolha:** `(curtidas + 2·comentários + 3·votos) / (horas + 2)^1.5`.
  Comentário e voto pesam mais por premiarem participação, e o post velho
  perde posição rápido. Detalhes e Big O em "Uma escolha técnica".
- **O que cortamos e por quê:** peso por número de seguidores do autor e
  recomendação personalizada. Os dois reintroduziriam a vantagem de quem já é
  famoso; as tags de interesse já personalizam o Explorar.

### 4. Perfil de artista e de leitor

- **Contexto:** quem desenha e quem lê têm papéis diferentes na rede.
- **Opções:** um tipo único de conta ou escolher no cadastro.
- **Escolha:** `tipo` na conta (artista ou leitor). Só artista cria história,
  publica capítulo e abre votação; os dois postam, comentam, curtem e votam. O
  artista ganha selo no perfil e nos posts.
- **O que cortamos e por quê:** trocar de tipo depois do cadastro e um terceiro
  papel (editor). Mantém a regra de permissão simples de testar.

## O que ficou de fora e por quê

- **Comissões terceirizadas** (pedir arte paga): é outro produto, um
  marketplace, com pagamento, prazo e disputa.
- **Eventos** (feiras, encontros): é outro produto, uma agenda.
- **Upload de imagem hospedado no deploy:** o filesystem do Render zera a cada
  restart; por isso o seed usa arquivos versionados em `frontend/public/seed/`.
- **Fóruns** entraram, mas só depois do núcleo e da jornada, e ficam fora do
  feed pessoal para não misturar conversa de grupo com a vitrine do artista.

## Features

Listem as features que o time vai construir, quem é o dono de cada uma e por
que ela entra no produto. A lista muda junto com o projeto: acrescentem e
tirem linhas quando mudarem de ideia.

| Feature | Dono | Por quê (1 frase) |
|---|---|---|
| Auth (núcleo) | Ryan | Sem login ninguém posta, vota nem comenta; é o gargalo de todo o time. |
| Posts (núcleo) | Matheus | O post é o conteúdo base: o feed mistura texto puro e arte (`imagem_url`), como no Twitter. |
| Feed (núcleo) | Laura | A prioridade no Feed sempre é de quem o usuário segue, mas também é intercalado conteúdo novo. |
| Perfil (núcleo) | Matheus | O artista precisa de uma vitrine própria; o perfil é onde o leitor conhece quem desenha (com selo de artista). |
| Follow (núcleo) | Matheus | Seguir um artista é como o leitor acompanha as histórias dele; também alimenta o feed dos seguidos. |
| Curtidas (núcleo) | Laura | Curtir um post mostra o conteúdo - posts e artistas - que os usuários gostam de ver, ajudando a balancear o feed. |
| Histórias em capítulos | Laura | É o formato central da rede: o artista publica a história em capítulos (páginas em sequência), não em posts soltos; cada capítulo novo vira um post no feed. |
| Tags de interesse e Explorar | Laura | O leitor encontra artistas novos pelo gênero que gosta sem depender de já seguir alguém: `#tags` nos posts alimentam um índice invertido (`core/tags.py`, tag → posts, O(1) para consultar e O(t) para indexar), o onboarding grava as tags favoritas e o Explorar mostra primeiro o que bate com elas. |
| Comentários (núcleo) | Ryan | O comentário é onde acontece a interação social da rede, sem eles não há engajamento e comunidade. |
| Seed fake (núcleo) | Claude (IA) + revisão do time | A demo nunca começa vazia e o nicho (quadrinistas e ilustradores iniciantes) já aparece no conteúdo. |
| Upload de arte | Ryan | Uma rede de artes sem imagem não existe; o upload transforma o post em obra. |
| Em alta | Ryan | Dá visibilidade a quem engaja agora, não a quem já é famoso: artista iniciante e veterano competem igual. |
| Fóruns | Matheus | Espaço para discutir técnica e histórias fora de um post específico; posts do fórum ficam em tabela própria e não entram no feed pessoal. |
| Escolha sua jornada | Matheus | É o diferencial da rede: o leitor vota na decisão do personagem e muda o rumo da história. |
| Deploy público | Matheus | A banca abre a URL e faz o fluxo completo; `SEED_ON_BOOT` e `CORS_ORIGINS` deixam o deploy reproduzível. |
| Upload de Imagens | Ryan | Os artistas precisam dar upload nas suas artes e trabalhos para visualização |

## Uma escolha técnica

Contem uma escolha técnica que o time fez e por quê. Por exemplo, por que usou
uma estrutura de dados no `core/`, qual o Big O da operação principal, ou o
que mudaria se a rede crescesse 100 vezes. Se mediram com `make bench`, colem a
saída e uma frase dizendo o que os números mostram.

### Escolha sua jornada: árvore da história (`core/jornada.py`)

Cada capítulo é um nó; as opções da decisão no fim dele são as arestas. A
opção vencedora aponta para o próximo capítulo, e as que não venceram ficam
guardadas só como texto ("o que poderia ter sido"). A estrutura é um
`dict[capitulo_id -> No]` mais um `dict[historia_id -> raiz]`, em Python puro,
e o endpoint `GET /historias/{id}/jornada` a usa para montar o mapa.

| Operação | Custo | Por quê |
|---|---|---|
| publicar capítulo / abrir decisão | O(1) | inserção em dict + um dict de filhos por opção |
| encerrar votação (calcula a vencedora) | O(k), k ≤ 4 → O(1) | máximo sobre no máximo 4 contagens |
| vencedora / encerrada / filho de uma opção | O(1) | lookup em hash |
| caminho tomado (mapa) | O(d), d = capítulos já percorridos | segue só a aresta vencedora; não olha os ramos mortos |
| reconstruir no startup | O(n) | uma passada nos capítulos e decisões do banco |

Sem a árvore, achar o caminho exigiria, a cada capítulo, buscar no banco a
decisão e contar os votos (d consultas por request). Com ela, o banco só é
consultado para votos ainda abertos. Não há timer: o encerramento é detectado
na primeira leitura ou escrita depois do prazo (`sincronizar`), que fecha o nó
em O(1). Empate vence a opção de menor índice; votação sem votos não tem
vencedora e a história para ali. Se a rede crescesse 100x, o dict em memória
continuaria O(1) por operação, mas ocuparia memória por capítulo; aí o índice
passaria para o banco.

### Em alta: heap top-K (`core/em_alta.py`)

`score = (curtidas + 2·comentários + 3·votos) / (horas + 2)^1.5`. Comentário e
voto pesam mais que curtida porque premiam discussão e participação, não só um
toque. O expoente 1,5 faz o post envelhecer rápido: 24 h depois ele precisa de
cerca de 47x o engajamento para ocupar o mesmo lugar. Votos de uma história
valem para os posts dela ("novo capítulo").

Como o score depende do relógio, um heap pronto ficaria velho. O que o `core/`
guarda são os contadores por post (dict), atualizados em O(1) a cada curtida,
comentário, voto ou post criado/apagado; o top-K sai de `heapq.nlargest` na
consulta.

| Operação | Custo |
|---|---|
| curtir / comentar / votar / criar / apagar | O(1) |
| página do Em alta (top-K, K = offset + limit) | O(n log K) |
| ordenar tudo (alternativa descartada) | O(n log n) |
| reconstruir no startup | O(n) |

`make bench` (K = 20, melhor de 5, ms): 1 000 posts 0,21 vs. 0,26; 10 000 posts
2,18 vs. 3,49; 100 000 posts 19,65 vs. 39,52. O heap fica ~2x mais rápido e a
diferença cresce com n, porque `nlargest` mantém só K itens em vez de ordenar
os n. Os dois ainda são lineares na leitura dos scores; num banco real seria um
índice ou cache com TTL.

## Uso de IA

Ferramenta e para quê. Exemplo: "Claude para gerar o seed de 200 posts sobre
corrida; o resto foi escrito pelo time."

Ryan: Claude para implementar a lógica de login, e criar conta, bem como diferenciar artista e leitor.
Matheus: Claude para implementar Posts, Seguir e Perfil (backend, testes e telas); revisão e decisões do time.
Laura: Claude para ajudar a implementar Curtidas e Feed e para corrigir revisões de código; Claude para implementar a seed fake e as Histórias em capítulos (backend, testes e telas).

Matheus: Claude para implementar o Em alta (core/em_alta.py, aba na home, testes e bench), os Fóruns e o deploy.

Matheus: Claude para implementar a feature Escolha sua jornada (decisões, votos, árvore em `core/jornada.py`, telas e testes).

Senha de todos os usuários do seed fake: `quadrinhos-123` (definida em `SENHA_SEED`, em `backend/scripts/seed.py`).
