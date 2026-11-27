# Decisões do time

**Time:** 
Maria Laura (@mlaurasarmentov)
Matheus Brito (@matheuscbrito)
Ryan Rodrigues (@RyanRodMat)

Este arquivo acompanha o projeto. Comecem com o que já sabem e atualizem quando
as decisões mudarem.

## Produto

Respondam antes de escolher features. O pitch sai daqui.

- **Público:** artistas pequenos que querem criar uma base de seguidores para suas artes / histórias.
- **Problema:** ao postar em redes sociais gerais, arte se perde entre algoritmos que priorizam quantidade à qualidade.
- **Como a rede resolve:** a rede reúne amantes de arte à artistas independentes e um feed em torno de seguidores, 
  garantindo qualidade.
- **Como saberíamos que funcionou:** vendo a criação de novas comunidades e fanbases em torno das histórias.

## Decisões de produto

Registrem de 3 a 5 escolhas que mudaram o que a rede é. Boas candidatas: por
que essas features e não outras, o que ficou de fora, como o seed e a interface
refletem o nicho. Uma delas vai para o vídeo.

### 1. Histórias em capítulos em vez de posts soltos

- **Contexto:** a rede é para artistas pequenos que querem formar uma base de leitores em torno de uma obra, e não só juntar curtidas em imagens avulsas.
- **Opções:** só posts (texto + imagem) como nas redes gerais, ou um formato próprio de história com capítulos e páginas em sequência.
- **Escolha:** a história é o formato central. O artista publica capítulos (páginas em ordem) e cada capítulo novo vira um post no feed, com comentários por capítulo.
- **O que cortamos e por quê:** ficou de fora um "álbum" ou galeria solta de ilustrações como entidade própria. Posts com imagem já cobrem esse caso, e o leitor volta por uma história para acompanhar, não por uma imagem isolada.

### 2. Feed por quem o usuário segue, sem "Em alta"

- **Contexto:** o problema que a rede resolve é a arte se perder em algoritmos que priorizam quantidade sobre qualidade.
- **Opções:** feed ranqueado por engajamento (curtidas) ou feed cronológico com prioridade para quem o usuário segue.
- **Escolha:** cronológico, mais novo primeiro, com posts de quem o usuário segue e de quem os seguidos seguem, intercalados com conteúdo novo. Curtidas ajudam a balancear o que aparece, mas não ordenam o feed.
- **O que cortamos e por quê:** o ranking por engajamento. Ele favorece quem já tem público, e a rede existe para dar espaço a quem está começando.

### 3. Escolha sua jornada: o leitor vota no rumo da história

- **Contexto:** queríamos algo que transformasse leitores em comunidade (o critério de sucesso é o surgimento de fanbases), não só espectadores.
- **Opções:** apenas curtidas e comentários, ou deixar o leitor votar numa decisão do personagem ao fim do capítulo.
- **Escolha:** o artista abre uma decisão com até 4 opções e prazo. A opção vencedora define o próximo capítulo, e as que perderam ficam registradas como "o que poderia ter sido". O mapa da jornada mostra o caminho tomado.
- **O que cortamos e por quê:** votação sem prazo e árvore ramificada completa, em que todos os ramos seriam escritos. Isso exigiria o artista produzir várias versões de cada capítulo. Só o ramo vencedor é escrito, o que é viável para um artista sozinho.

### 4. Explorar por tags de interesse, sem depender de já seguir alguém

- **Contexto:** um leitor novo não segue ninguém e o feed por seguidos começaria vazio.
- **Opções:** busca por texto livre, categorias fixas ou `#tags` nos posts com o leitor escolhendo seus gêneros no onboarding.
- **Escolha:** `#tags` nos posts alimentam um índice invertido (`core/tags.py`). O onboarding grava as tags favoritas e o Explorar mostra primeiro o que bate com elas.
- **O que cortamos e por quê:** a busca textual completa e as recomendações personalizadas por comportamento. As tags declaradas pelo próprio leitor resolvem o começo frio com bem menos complexidade.

### 5. Upload de imagens validado e com limite, em vez de só URL externa

- **Contexto:** o artista precisa publicar a própria arte, e colar o link de uma imagem hospedada em outro lugar é uma barreira para quem está começando.
- **Opções:** aceitar só `imagem_url` externa, ou receber o arquivo direto na API.
- **Escolha:** upload direto de jpg, png ou webp de até 2 MB. O servidor confere o tipo e a assinatura real do arquivo (não confia só no `Content-Type`), grava com nome aleatório e apaga o arquivo se o post for removido ou falhar.
- **O que cortamos e por quê:** formatos como GIF e arquivos grandes, para evitar abuso de armazenamento. As imagens do seed ficam versionadas no front (`/seed/`), porque a pasta `uploads/` não sobrevive ao deploy.

Exemplo:

> **Feed cronológico em vez de "Em alta"**
>
> - **Contexto:** a comunidade é de corredores que treinam juntos.
> - **Opções:** feed ranqueado por engajamento ou feed cronológico.
> - **Escolha:** cronológico, com stories do dia.
> - **O que cortamos e por quê:** o "Em alta". Quem abre o app quer ver o
>   treino de hoje dos amigos, não o post mais curtido da semana.

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
| Escolha sua jornada | Matheus | É o diferencial da rede: o leitor vota na decisão do personagem e muda o rumo da história. |
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

## Uso de IA

Ferramenta e para quê. Exemplo: "Claude para gerar o seed de 200 posts sobre
corrida; o resto foi escrito pelo time."

Ryan: Claude para implementar a lógica de login, e criar conta, bem como diferenciar artista e leitor.
Matheus: Claude para implementar Posts, Seguir e Perfil (backend, testes e telas); revisão e decisões do time.
Laura: Claude para ajudar a implementar Curtidas e Feed e para corrigir revisões de código; Claude para implementar a seed fake e as Histórias em capítulos (backend, testes e telas).

Ryan: Claude para implementar Comentários (posts e capítulos) e o Upload de Imagens (validação, limpeza de arquivos, backend, testes e telas), além da configuração de deploy (`SEED_ON_BOOT`, `CORS_ORIGINS`).

Matheus: Claude para implementar a feature Escolha sua jornada (decisões, votos, árvore em `core/jornada.py`, telas e testes).

Senha de todos os usuários do seed fake: `quadrinhos-123` (definida em `SENHA_SEED`, em `backend/scripts/seed.py`).
