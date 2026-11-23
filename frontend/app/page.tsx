"use client";

import { useCallback, useEffect, useState } from "react";

import { NovoPost } from "@/components/NovoPost";
import { PostCard } from "@/components/PostCard";
import { apiGet, type Page, type Post } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

const POR_PAGINA = 10;

export default function Home() {
  useExigeLogin();
  const [posts, setPosts] = useState<Post[]>([]);
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  // Provisório: posts recentes de todo mundo. O feed dos seguidos (GET /feed) é outra issue.
  const carregar = useCallback(async (offset: number) => {
    setCarregando(true);
    try {
      const pagina = await apiGet<Page<Post>>(`/posts?offset=${offset}&limit=${POR_PAGINA}`);
      setPosts((atuais) => (offset === 0 ? pagina.items : [...atuais, ...pagina.items]));
      setTotal(pagina.total);
      setErro(null);
    } catch {
      setErro("não consegui carregar os posts — o backend está rodando?");
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    if (localStorage.getItem("token")) carregar(0);
  }, [carregar]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Feed</h1>
      {/* a caixa fica sempre visível; ao publicar, o post entra no topo da lista */}
      <NovoPost
        onCriado={(post) => {
          setPosts((atuais) => [post, ...atuais]);
          setTotal((t) => t + 1);
        }}
      />

      {erro && <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</p>}

      <ul className="space-y-3">
        {posts.map((p) => (
          <li key={p.id}>
            <PostCard post={p} />
          </li>
        ))}
      </ul>

      {!carregando && !erro && posts.length === 0 && (
        <p className="text-zinc-500">Ainda não há posts. Publique o primeiro!</p>
      )}
      {posts.length < total && (
        <button
          onClick={() => carregar(posts.length)}
          disabled={carregando}
          className="rounded border bg-white px-3 py-1.5 text-sm disabled:opacity-50"
        >
          {carregando ? "carregando..." : "carregar mais"}
        </button>
      )}
    </div>
  );
}
