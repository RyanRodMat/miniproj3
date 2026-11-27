"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useState } from "react";

import { PostCard } from "@/components/PostCard";
import { apiGet, type Page, type Post, type TagContagem, type User } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

const POR_PAGINA = 10;

function Explorar() {
  useExigeLogin();
  const tag = useSearchParams().get("tag")?.toLowerCase() ?? "";
  const [tags, setTags] = useState<TagContagem[]>([]);
  const [eu, setEu] = useState<User>();
  const [posts, setPosts] = useState<Post[]>([]);
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  const carregar = useCallback(
    async (offset: number) => {
      setCarregando(true);
      try {
        const filtro = tag ? `&tag=${encodeURIComponent(tag)}` : "";
        const pagina = await apiGet<Page<Post>>(`/explorar?offset=${offset}&limit=${POR_PAGINA}${filtro}`);
        setPosts((atuais) => (offset === 0 ? pagina.items : [...atuais, ...pagina.items]));
        setTotal(pagina.total);
        setErro(null);
      } catch {
        setErro("não consegui carregar o Explorar — o backend está rodando?");
      } finally {
        setCarregando(false);
      }
    },
    [tag],
  );

  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    apiGet<{ items: TagContagem[] }>("/tags?limit=20").then((r) => setTags(r.items)).catch(() => {});
    apiGet<User>("/auth/eu").then(setEu).catch(() => {});
  }, []);

  useEffect(() => {
    if (localStorage.getItem("token")) carregar(0);
  }, [carregar]);

  const interesses = new Set(eu?.tags_interesse ?? []);
  // as tags de interesse do usuário vêm primeiro nos chips
  const chips = [...tags].sort((a, b) => Number(interesses.has(b.tag)) - Number(interesses.has(a.tag)));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Explorar{tag && ` · #${tag}`}</h1>

      <div className="flex flex-wrap gap-2">
        <Link
          href="/explorar"
          className={`rounded-full border px-3 py-1 text-sm ${
            !tag ? "border-zinc-900 bg-zinc-900 text-white" : "border-zinc-300 bg-white hover:bg-zinc-100"
          }`}
        >
          Para você
        </Link>
        {chips.map((t) => (
          <Link
            key={t.tag}
            href={`/explorar?tag=${t.tag}`}
            className={`rounded-full border px-3 py-1 text-sm ${
              tag === t.tag
                ? "border-zinc-900 bg-zinc-900 text-white"
                : interesses.has(t.tag)
                  ? "border-amber-400 bg-amber-100 hover:bg-amber-200"
                  : "border-zinc-300 bg-white hover:bg-zinc-100"
            }`}
          >
            #{t.tag} <span className="text-xs opacity-70">{t.contagem}</span>
          </Link>
        ))}
      </div>
      {!tag && interesses.size > 0 && (
        <p className="text-sm text-zinc-500">Posts das suas tags de interesse aparecem primeiro.</p>
      )}

      {erro && <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</p>}

      <ul className="space-y-3">
        {posts.map((p) => (
          <li key={p.id}>
            <PostCard post={p} euId={eu?.id} />
          </li>
        ))}
      </ul>

      {!carregando && !erro && posts.length === 0 && (
        <p className="text-zinc-500">Nenhum post {tag ? `com #${tag}` : "por aqui"} ainda.</p>
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

export default function ExplorarPage() {
  return (
    <Suspense>
      <Explorar />
    </Suspense>
  );
}
