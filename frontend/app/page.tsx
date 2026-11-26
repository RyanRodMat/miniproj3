"use client";

import { useCallback, useEffect, useState } from "react";

import { NovoPost } from "@/components/NovoPost";
import { PostCard } from "@/components/PostCard";
import { apiGet, type Page, type Post, type User } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

const POR_PAGINA = 10;

export default function Home() {
  useExigeLogin();
  const [posts, setPosts] = useState<Post[]>([]);
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [euId, setEuId] = useState<number>();
  const [publicado, setPublicado] = useState(false);

  const carregar = useCallback(async (offset: number) => {
    setCarregando(true);
    try {
      const pagina = await apiGet<Page<Post>>(`/feed?offset=${offset}&limit=${POR_PAGINA}`);
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
    if (localStorage.getItem("token")) {
      carregar(0);
      apiGet<User>("/auth/eu").then((u) => setEuId(u.id)).catch(() => {});
    }
  }, [carregar]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Feed</h1>
      {/* o feed só tem quem você segue: o post novo aparece no seu perfil, não aqui */}
      <NovoPost onCriado={() => setPublicado(true)} />
      {publicado && <p className="text-sm text-green-700">Publicado! Ele aparece no seu perfil.</p>}

      {erro && <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</p>}

      <ul className="space-y-3">
        {posts.map((p) => (
          <li key={p.id}>
            <PostCard post={p} euId={euId} />
          </li>
        ))}
      </ul>

      {!carregando && !erro && posts.length === 0 && (
        <p className="text-zinc-500">Seu feed está vazio. Siga alguém na página de usuários para ver os posts aqui.</p>
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
