"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { apiGet, apiPost, type Comentario, type Page } from "@/lib/api";

const POR_PAGINA = 20;

// O SQLite devolve datas sem fuso (sem o "Z"); sem isso o navegador as lê como horário local.
function formatarData(iso: string): string {
  const comFuso = /(Z|[+-]\d\d:?\d\d)$/.test(iso) ? iso : `${iso}Z`;
  return new Date(comFuso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

export function Comentarios({ alvo, id }: { alvo: "posts" | "capitulos"; id: number }) {
  const caminho = `/${alvo}/${id}/comentarios`;

  const [itens, setItens] = useState<Comentario[]>([]);
  const [novos, setNovos] = useState<Comentario[]>([]);
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erroLista, setErroLista] = useState<string | null>(null);

  const [texto, setTexto] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;
    setCarregando(true);
    setErroLista(null);
    apiGet<Page<Comentario>>(`${caminho}?offset=0&limit=${POR_PAGINA}`)
      .then((p) => {
        if (cancelado) return;
        setItens(p.items);
        setTotal(p.total);
      })
      .catch((e) => {
        if (!cancelado) setErroLista(e instanceof Error ? e.message : "erro ao carregar");
      })
      .finally(() => {
        if (!cancelado) setCarregando(false);
      });
    return () => {
      cancelado = true;
    };
  }, [caminho]);

  async function carregarMais() {
    setCarregando(true);
    try {
      const p = await apiGet<Page<Comentario>>(`${caminho}?offset=${itens.length}&limit=${POR_PAGINA}`);
      setItens((atual) => [...atual, ...p.items]);
      setTotal(p.total);
    } catch (e) {
      setErroLista(e instanceof Error ? e.message : "erro ao carregar");
    } finally {
      setCarregando(false);
    }
  }

  async function comentar(e: React.FormEvent) {
    e.preventDefault();
    setEnviando(true);
    setErro(null);
    try {
      const novo = await apiPost<Comentario>(caminho, { texto });
      // a lista é cronológica: o novo vai no fim. Guardado à parte para aparecer já,
      // mesmo com páginas por carregar; sai daqui quando o "carregar mais" chegar nele.
      setNovos((atual) => [...atual, novo]);
      setTotal((t) => t + 1);
      setTexto("");
    } catch (err) {
      setErro(err instanceof Error ? err.message : "erro ao comentar");
    } finally {
      setEnviando(false);
    }
  }

  const pendentes = novos.filter((n) => !itens.some((i) => i.id === n.id));
  const visiveis = [...itens, ...pendentes];
  const faltam = total - visiveis.length;

  return (
    <section className="space-y-3">
      <h2 className="text-lg font-semibold">Comentários ({total})</h2>

      <form onSubmit={comentar} className="space-y-2 rounded-lg border bg-white p-3">
        <textarea
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Escreva um comentário..."
          required
          maxLength={2000}
          rows={2}
          className="w-full rounded border px-2 py-1"
        />
        {erro && <p className="text-sm text-red-700">{erro}</p>}
        <button
          type="submit"
          disabled={enviando || !texto.trim()}
          className="rounded bg-zinc-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
        >
          {enviando ? "enviando..." : "comentar"}
        </button>
      </form>

      {erroLista && <p className="text-sm text-red-700">{erroLista}</p>}

      <ul className="space-y-2">
        {visiveis.map((c) => (
          <li key={c.id} className="rounded-lg border bg-white p-3">
            <div className="flex items-baseline gap-2 text-sm">
              <Link href={`/u/${c.autor.username}`} className="font-medium hover:underline">
                {c.autor.name}
              </Link>
              <span className="text-zinc-500">@{c.autor.username}</span>
              <span className="ml-auto text-xs text-zinc-500">{formatarData(c.criado_em)}</span>
            </div>
            <p className="mt-1 whitespace-pre-wrap">{c.texto}</p>
          </li>
        ))}
      </ul>

      {!carregando && !erroLista && visiveis.length === 0 && (
        <p className="text-sm text-zinc-500">Nenhum comentário ainda. Seja a primeira pessoa a comentar.</p>
      )}

      {carregando && <p className="text-sm text-zinc-500">carregando...</p>}

      {!carregando && faltam > 0 && (
        <button onClick={carregarMais} className="rounded border px-3 py-1.5 text-sm">
          carregar mais
        </button>
      )}
    </section>
  );
}