import Link from "next/link";

import { BotaoCurtir } from "@/components/BotaoCurtir";
import { BotaoSeguir } from "@/components/BotaoSeguir";
import { ComentariosDoPost } from "@/components/ComentariosDoPost";
import { TextoComTags } from "@/components/TextoComTags";
import type { Post } from "@/lib/api";

/**
 * Renderiza texto puro OU texto + arte, conforme `imagem_url`.
 * Com `euId`, mostra o botão de seguir o autor (some nos posts do próprio usuário).
 * `comentarios={false}` esconde o botão de comentários (a página do post já lista os dela).
 */
export function PostCard({ post, euId, comentarios = true }: { post: Post; euId?: number; comentarios?: boolean }) {
  return (
    <article className="space-y-3 rounded-lg border bg-white p-4">
      <header className="flex items-center gap-2 text-sm">
        <Link href={`/u/${post.autor.username}`} className="flex items-center gap-2 hover:underline">
          <span className="font-medium">{post.autor.name}</span>
          <span className="text-zinc-500">@{post.autor.username}</span>
        </Link>
        {post.autor.tipo === "artista" && (
          <span className="rounded bg-amber-100 px-1.5 py-0.5 text-xs text-amber-800">artista</span>
        )}
        {euId !== undefined && euId !== post.autor.id && (
          <BotaoSeguir username={post.autor.username} seguindoInicial={post.autor_eu_sigo} />
        )}
        <Link href={`/posts/${post.id}`} className="ml-auto text-xs text-zinc-400 hover:underline">
          <time dateTime={post.created_at}>{new Date(post.created_at).toLocaleString("pt-BR")}</time>
        </Link>
      </header>
      <p className="whitespace-pre-wrap">
        <TextoComTags texto={post.texto} />
      </p>
      {post.imagem_url && (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={post.imagem_url} alt="" className="max-h-[32rem] w-full rounded object-contain" />
      )}
      {post.historia_id !== null && (
        <Link href={`/historias/${post.historia_id}`} className="block text-sm text-amber-800 hover:underline">
          ler a história →
        </Link>
      )}
      {comentarios ? (
        <ComentariosDoPost postId={post.id}>
          <BotaoCurtir postId={post.id} curtidasInicial={post.curtidas} curtiuInicial={post.eu_curti} />
        </ComentariosDoPost>
      ) : (
        <BotaoCurtir postId={post.id} curtidasInicial={post.curtidas} curtiuInicial={post.eu_curti} />
      )}
    </article>
  );
}
