"use client";
import { Comentarios } from "@/components/Comentarios";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { PostCard } from "@/components/PostCard";
import { ApiError, apiDelete, apiGet, apiPatch, type Post, type User } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

export default function PostPage() {
  useExigeLogin();
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [post, setPost] = useState<Post | null>(null);
  const [eu, setEu] = useState<User | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [editando, setEditando] = useState(false);
  const [texto, setTexto] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    apiGet<Post>(`/posts/${id}`)
      .then(setPost)
      .catch((e) =>
        setErro(e instanceof ApiError && e.status === 404 ? "post não encontrado" : "erro ao carregar o post")
      );
    apiGet<User>("/auth/eu").then(setEu).catch(() => {});
  }, [id]);

  async function salvar(e: React.FormEvent) {
    e.preventDefault();
    try {
      setPost(await apiPatch<Post>(`/posts/${id}`, { texto }));
      setEditando(false);
      setErro(null);
    } catch (err) {
      setErro(err instanceof Error ? err.message : "erro ao salvar");
    }
  }

  async function apagar() {
    if (!confirm("Apagar este post?")) return;
    try {
      await apiDelete(`/posts/${id}`);
      router.push("/");
    } catch (err) {
      setErro(err instanceof Error ? err.message : "erro ao apagar");
    }
  }

  const ehAutor = !!post && !!eu && post.autor.id === eu.id;

  return (
    <div className="space-y-4">
      {erro && <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</p>}
      {post && !editando && <PostCard post={post} euId={eu?.id} />}
      {post && editando && (
        <form onSubmit={salvar} className="space-y-2 rounded-lg border bg-white p-3">
          <textarea
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            required
            maxLength={2000}
            rows={4}
            className="w-full rounded border px-2 py-1"
          />
          <div className="flex gap-2 text-sm">
            <button type="submit" className="rounded bg-zinc-900 px-3 py-1.5 text-white">
              salvar
            </button>
            <button type="button" onClick={() => setEditando(false)} className="px-3 py-1.5 text-zinc-600">
              cancelar
            </button>
          </div>
        </form>
      )}
      {ehAutor && !editando && (
        <div className="flex gap-4 text-sm">
          <button
            onClick={() => {
              setTexto(post!.texto);
              setEditando(true);
            }}
            className="text-zinc-600 hover:text-zinc-900"
          >
            editar
          </button>
          <button onClick={apagar} className="text-red-700 hover:text-red-900">
            apagar
          </button>
        </div>
      )}
      {post && <Comentarios alvo="posts" id={post.id} />} 
    </div>
  );
}
