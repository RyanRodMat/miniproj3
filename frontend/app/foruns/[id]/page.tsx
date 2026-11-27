"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { apiGet, apiPost, type Forum, type ForumPost, type Page } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

const POR_PAGINA = 10;

export default function PaginaForum() {
  useExigeLogin();
  const { id } = useParams<{ id: string }>();
  const [forum, setForum] = useState<Forum>();
  const [posts, setPosts] = useState<ForumPost[]>([]);
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [texto, setTexto] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [erroPost, setErroPost] = useState<string | null>(null);

  const carregarPosts = useCallback(
    async (offset: number) => {
      setCarregando(true);
      try {
        const pagina = await apiGet<Page<ForumPost>>(`/foruns/${id}/posts?offset=${offset}&limit=${POR_PAGINA}`);
        setPosts((atuais) => (offset === 0 ? pagina.items : [...atuais, ...pagina.items]));
        setTotal(pagina.total);
      } catch {
        setErro("não consegui carregar as mensagens");
      } finally {
        setCarregando(false);
      }
    },
    [id],
  );

  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    apiGet<Forum>(`/foruns/${id}`)
      .then((f) => {
        setForum(f);
        setErro(null);
      })
      .catch(() => setErro("fórum não encontrado"));
    carregarPosts(0);
  }, [id, carregarPosts]);

  async function alternarEntrada() {
    if (!forum) return;
    const entrar = !forum.sou_membro;
    try {
      await apiPost(`/foruns/${id}/${entrar ? "entrar" : "sair"}`);
      setForum({ ...forum, sou_membro: entrar, membros: forum.membros + (entrar ? 1 : -1) });
    } catch {
      setErro("não consegui atualizar sua participação");
    }
  }

  async function postar(e: React.FormEvent) {
    e.preventDefault();
    setEnviando(true);
    setErroPost(null);
    try {
      await apiPost<ForumPost>(`/foruns/${id}/posts`, { texto });
      setTexto("");
      await carregarPosts(0);
    } catch (err) {
      setErroPost(err instanceof Error ? err.message : "erro ao publicar");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="space-y-6">
      <Link href="/foruns" className="text-sm text-zinc-500 hover:underline">
        ← fóruns
      </Link>

      {erro && <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</p>}

      {forum && (
        <header className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">{forum.nome}</h1>
            <button
              onClick={alternarEntrada}
              className={`ml-auto rounded px-3 py-1.5 text-sm ${
                forum.sou_membro ? "border bg-white" : "bg-zinc-900 text-white"
              }`}
            >
              {forum.sou_membro ? "sair do fórum" : "entrar"}
            </button>
          </div>
          {forum.descricao && <p className="text-zinc-600">{forum.descricao}</p>}
          <p className="text-xs text-zinc-500">
            {forum.membros} {forum.membros === 1 ? "membro" : "membros"}
          </p>
        </header>
      )}

      {forum?.sou_membro ? (
        <form onSubmit={postar} className="space-y-2 rounded-lg border bg-white p-3">
          <textarea
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder="Escreva para o fórum"
            required
            maxLength={2000}
            rows={3}
            className="w-full rounded border px-2 py-1"
          />
          {erroPost && <p className="text-sm text-red-700">{erroPost}</p>}
          <button
            type="submit"
            disabled={enviando}
            className="rounded bg-zinc-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
          >
            {enviando ? "publicando..." : "publicar"}
          </button>
        </form>
      ) : (
        forum && <p className="text-sm text-zinc-500">Entre no fórum para participar da conversa.</p>
      )}

      <ul className="space-y-3">
        {posts.map((p) => (
          <li key={p.id} className="space-y-1 rounded-lg border bg-white p-4">
            <header className="flex items-center gap-2 text-sm">
              <Link href={`/u/${p.autor.username}`} className="font-medium hover:underline">
                {p.autor.name}
              </Link>
              <span className="text-zinc-500">@{p.autor.username}</span>
              <time dateTime={p.created_at} className="ml-auto text-xs text-zinc-400">
                {new Date(p.created_at).toLocaleString("pt-BR")}
              </time>
            </header>
            <p className="whitespace-pre-wrap">{p.texto}</p>
          </li>
        ))}
      </ul>

      {!carregando && !erro && posts.length === 0 && <p className="text-zinc-500">Ninguém escreveu aqui ainda.</p>}
      {posts.length < total && (
        <button
          onClick={() => carregarPosts(posts.length)}
          disabled={carregando}
          className="rounded border bg-white px-3 py-1.5 text-sm disabled:opacity-50"
        >
          {carregando ? "carregando..." : "carregar mais"}
        </button>
      )}
    </div>
  );
}
