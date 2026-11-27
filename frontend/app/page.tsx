"use client";

import { useCallback, useEffect, useState } from "react";

import { NovoPost } from "@/components/NovoPost";
import { PostCard } from "@/components/PostCard";
import { apiGet, type Page, type Post, type User } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

const POR_PAGINA = 10;

type Aba = "seguindo" | "em-alta";
const ROTA: Record<Aba, string> = { seguindo: "/feed", "em-alta": "/em-alta" };

export default function Home() {
  useExigeLogin();
  const [aba, setAba] = useState<Aba>("seguindo");
  const [posts, setPosts] = useState<Post[]>([]);
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [euId, setEuId] = useState<number>();
  const [publicado, setPublicado] = useState(false);

  const carregar = useCallback(
    async (offset: number) => {
    setCarregando(true);
    try {
      const pagina = await apiGet<Page<Post>>(`${ROTA[aba]}?offset=${offset}&limit=${POR_PAGINA}`);
      setPosts((atuais) => (offset === 0 ? pagina.items : [...atuais, ...pagina.items]));
      setTotal(pagina.total);
      setErro(null);
    } catch {
      setErro("não consegui carregar os posts — o backend está rodando?");
    } finally {
      setCarregando(false);
    }
    },
    [aba],
  );

  useEffect(() => {
    if (localStorage.getItem("token")) {
      setPosts([]);
      setTotal(0);
      carregar(0);
    }
  }, [carregar]);

  useEffect(() => {
    if (localStorage.getItem("token")) {
      apiGet<User>("/auth/eu").then((u) => setEuId(u.id)).catch(() => {});
    }
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex gap-2" role="tablist">
        {(
          [
            ["seguindo", "Seguindo"],
            ["em-alta", "Em alta"],
          ] as const
        ).map(([id, rotulo]) => (
          <button
            key={id}
            role="tab"
            aria-selected={aba === id}
            onClick={() => setAba(id)}
            className={`rounded-full border px-4 py-1.5 text-sm ${
              aba === id ? "border-zinc-900 bg-zinc-900 text-white" : "border-zinc-300 bg-white hover:bg-zinc-100"
            }`}
          >
            {rotulo}
          </button>
        ))}
      </div>
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
        <p className="text-zinc-500">
          {aba === "em-alta"
            ? "Nada em alta por enquanto."
            : "Seu feed está vazio. Siga alguém na página de usuários para ver os posts aqui."}
        </p>
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
