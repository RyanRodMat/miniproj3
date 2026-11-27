"use client";

import { useCallback, useEffect, useState } from "react";

import { NovoPost } from "@/components/NovoPost";
import { PostCard } from "@/components/PostCard";
import { EVENTO_SEGUINDO } from "@/components/SidebarSeguindo";
import { apiGet, type Page, type Post, type User } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

const POR_PAGINA = 10;

type Aba = "seguindo" | "para-voce";
const ABAS: { id: Aba; titulo: string; rota: string }[] = [
  { id: "seguindo", titulo: "Seguindo", rota: "/feed" },
  { id: "para-voce", titulo: "Para você", rota: "/explorar" },
];

type Feed = { posts: Post[]; total: number; carregando: boolean; erro: string | null };
const FEED_VAZIO: Feed = { posts: [], total: 0, carregando: true, erro: null };

export default function Home() {
  useExigeLogin();
  // um feed por aba, carregados juntos: trocar de aba só muda qual deles aparece
  const [feeds, setFeeds] = useState<Record<Aba, Feed>>({ seguindo: FEED_VAZIO, "para-voce": FEED_VAZIO });
  const [euId, setEuId] = useState<number>();
  const [publicado, setPublicado] = useState(false);
  const [aba, setAba] = useState<Aba>("seguindo");

  const { posts, total, carregando, erro } = feeds[aba];

  const carregar = useCallback(async (id: Aba, offset: number) => {
    const atualizar = (f: Partial<Feed>) => setFeeds((atuais) => ({ ...atuais, [id]: { ...atuais[id], ...f } }));
    atualizar({ carregando: true });
    try {
      const rota = ABAS.find((a) => a.id === id)!.rota;
      const pagina = await apiGet<Page<Post>>(`${rota}?offset=${offset}&limit=${POR_PAGINA}`);
      setFeeds((atuais) => ({
        ...atuais,
        [id]: {
          posts: offset === 0 ? pagina.items : [...atuais[id].posts, ...pagina.items],
          total: pagina.total,
          carregando: false,
          erro: null,
        },
      }));
    } catch {
      atualizar({ carregando: false, erro: "não consegui carregar os posts — o backend está rodando?" });
    }
  }, []);

  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    ABAS.forEach((a) => carregar(a.id, 0));
    apiGet<User>("/auth/eu").then((u) => setEuId(u.id)).catch(() => {});
  }, [carregar]);

  // seguir/deixar de seguir muda o que o feed "Seguindo" mostra
  useEffect(() => {
    const recarregar = () => carregar("seguindo", 0);
    window.addEventListener(EVENTO_SEGUINDO, recarregar);
    return () => window.removeEventListener(EVENTO_SEGUINDO, recarregar);
  }, [carregar]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Feed</h1>
      {/* o feed só tem quem você segue: o post novo aparece no seu perfil, não aqui */}
      <NovoPost onCriado={() => setPublicado(true)} />
      {publicado && <p className="text-sm text-green-700">Publicado! Ele aparece no seu perfil.</p>}

      <div role="tablist" className="flex gap-6 border-b border-zinc-200">
        {ABAS.map((a) => (
          <button
            key={a.id}
            role="tab"
            aria-selected={aba === a.id}
            onClick={() => setAba(a.id)}
            className={`-mb-px border-b-2 px-1 pb-2 text-sm font-medium ${
              aba === a.id
                ? "border-zinc-900 text-zinc-900"
                : "border-transparent text-zinc-500 hover:text-zinc-900"
            }`}
          >
            {a.titulo}
          </button>
        ))}
      </div>

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
          {aba === "seguindo"
            ? "Seu feed está vazio. Siga alguém na página de usuários para ver os posts aqui."
            : "Nenhum post por aqui ainda."}
        </p>
      )}
      {posts.length < total && (
        <button
          onClick={() => carregar(aba, posts.length)}
          disabled={carregando}
          className="rounded border bg-white px-3 py-1.5 text-sm disabled:opacity-50"
        >
          {carregando ? "carregando..." : "carregar mais"}
        </button>
      )}
    </div>
  );
}
