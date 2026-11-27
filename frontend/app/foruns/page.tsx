"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { apiGet, apiPost, type Forum, type Page } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

const POR_PAGINA = 10;

export default function Foruns() {
  useExigeLogin();
  const [foruns, setForuns] = useState<Forum[]>([]);
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [nome, setNome] = useState("");
  const [descricao, setDescricao] = useState("");
  const [criando, setCriando] = useState(false);
  const [erroCriar, setErroCriar] = useState<string | null>(null);

  const carregar = useCallback(async (offset: number) => {
    setCarregando(true);
    try {
      const pagina = await apiGet<Page<Forum>>(`/foruns?offset=${offset}&limit=${POR_PAGINA}`);
      setForuns((atuais) => (offset === 0 ? pagina.items : [...atuais, ...pagina.items]));
      setTotal(pagina.total);
      setErro(null);
    } catch {
      setErro("não consegui carregar os fóruns — o backend está rodando?");
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    if (localStorage.getItem("token")) carregar(0);
  }, [carregar]);

  async function criar(e: React.FormEvent) {
    e.preventDefault();
    setCriando(true);
    setErroCriar(null);
    try {
      await apiPost<Forum>("/foruns", { nome, descricao });
      setNome("");
      setDescricao("");
      await carregar(0);
    } catch (err) {
      setErroCriar(err instanceof Error ? err.message : "erro ao criar o fórum");
    } finally {
      setCriando(false);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Fóruns</h1>

      <form onSubmit={criar} className="space-y-2 rounded-lg border bg-white p-3">
        <input
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          placeholder="Nome do novo fórum"
          required
          maxLength={60}
          className="w-full rounded border px-2 py-1"
        />
        <input
          value={descricao}
          onChange={(e) => setDescricao(e.target.value)}
          placeholder="Sobre o que se conversa aqui? (opcional)"
          maxLength={300}
          className="w-full rounded border px-2 py-1 text-sm"
        />
        {erroCriar && <p className="text-sm text-red-700">{erroCriar}</p>}
        <button
          type="submit"
          disabled={criando}
          className="rounded bg-zinc-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
        >
          {criando ? "criando..." : "criar fórum"}
        </button>
      </form>

      {erro && <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</p>}

      <ul className="space-y-3">
        {foruns.map((f) => (
          <li key={f.id}>
            <Link href={`/foruns/${f.id}`} className="block rounded-lg border bg-white p-4 hover:bg-zinc-50">
              <div className="flex items-center gap-2">
                <span className="font-medium">{f.nome}</span>
                {f.sou_membro && (
                  <span className="rounded bg-amber-100 px-1.5 py-0.5 text-xs text-amber-800">membro</span>
                )}
                <span className="ml-auto text-xs text-zinc-500">
                  {f.membros} {f.membros === 1 ? "membro" : "membros"}
                </span>
              </div>
              {f.descricao && <p className="mt-1 text-sm text-zinc-600">{f.descricao}</p>}
            </Link>
          </li>
        ))}
      </ul>

      {!carregando && !erro && foruns.length === 0 && (
        <p className="text-zinc-500">Nenhum fórum ainda. Crie o primeiro acima.</p>
      )}
      {foruns.length < total && (
        <button
          onClick={() => carregar(foruns.length)}
          disabled={carregando}
          className="rounded border bg-white px-3 py-1.5 text-sm disabled:opacity-50"
        >
          {carregando ? "carregando..." : "carregar mais"}
        </button>
      )}
    </div>
  );
}
