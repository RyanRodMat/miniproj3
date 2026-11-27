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

### 1. _Marte_

- **Contexto:** _(o que estava em jogo)_
- **Opções:** _(o que vocês consideraram)_
- **Escolha:** _(o que fizeram)_
- **O que cortamos e por quê:** _(o custo da escolha)_

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
| Comentários (núcleo) | | |
| Seed fake (núcleo) | Claude (IA) + revisão do time | A demo nunca começa vazia e o nicho (quadrinistas e ilustradores iniciantes) já aparece no conteúdo. |

## Uma escolha técnica

Contem uma escolha técnica que o time fez e por quê. Por exemplo, por que usou
uma estrutura de dados no `core/`, qual o Big O da operação principal, ou o
que mudaria se a rede crescesse 100 vezes. Se mediram com `make bench`, colem a
saída e uma frase dizendo o que os números mostram.

## Uso de IA

Ferramenta e para quê. Exemplo: "Claude para gerar o seed de 200 posts sobre
corrida; o resto foi escrito pelo time."

Ryan: Claude para implementar a lógica de login, e criar conta, bem como diferenciar artista e leitor.
Matheus: Claude para implementar Posts, Seguir e Perfil (backend, testes e telas); revisão e decisões do time.
Laura: Claude para ajudar a implementar Curtidas e Feed e para corrigir revisões de código; Claude para implementar a seed fake e as Histórias em capítulos (backend, testes e telas).

Senha de todos os usuários do seed fake: `quadrinhos-123` (definida em `SENHA_SEED`, em `backend/scripts/seed.py`).
