"use client";

import { useEffect, useState } from "react";

import { apiGet, apiPost, type Decisao } from "@/lib/api";

function restante(prazo: string, agora: number): string {
  const s = Math.max(0, Math.floor((new Date(prazo).getTime() - agora) / 1000));
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}min`;
  return `${m}min ${String(s % 60).padStart(2, "0")}s`;
}

/** Bloco de votação do fim do capítulo: barras de %, "já votei" e contagem regressiva. */
export function BlocoVotacao({ decisaoId, aoEncerrar }: { decisaoId: number; aoEncerrar?: () => void }) {
  const [d, setD] = useState<Decisao | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState(false);
  const [agora, setAgora] = useState(() => Date.now());

  useEffect(() => {
    apiGet<Decisao>(`/decisoes/${decisaoId}`)
      .then(setD)
      .catch((e) => setErro(e instanceof Error ? e.message : "erro ao carregar"));
  }, [decisaoId]);

  const aberta = !!d && !d.encerrada && new Date(d.prazo).getTime() > agora;

  useEffect(() => {
    if (!aberta) return;
    const t = setInterval(() => setAgora(Date.now()), 1000);
    return () => clearInterval(t);
  }, [aberta]);

  // o prazo acabou com a página aberta: busca o resultado final (o backend fecha na leitura)
  const venceu = !!d && !d.encerrada && new Date(d.prazo).getTime() <= agora;
  useEffect(() => {
    if (!venceu) return;
    apiGet<Decisao>(`/decisoes/${decisaoId}`).then((x) => {
      setD(x);
      aoEncerrar?.();
    });
  }, [venceu, decisaoId, aoEncerrar]);

  async function votar(opcao: number) {
    setOcupado(true);
    setErro(null);
    try {
      setD(await apiPost<Decisao>(`/decisoes/${decisaoId}/votar`, { opcao }));
    } catch (e) {
      setErro(e instanceof Error ? e.message : "erro ao votar");
    } finally {
      setOcupado(false);
    }
  }

  if (!d) return erro ? <p className="text-sm text-red-700">{erro}</p> : null;

  return (
    <section className="space-y-3 rounded-lg border bg-white p-4">
      <h2 className="font-medium">{d.pergunta}</h2>
      <ul className="space-y-2">
        {d.opcoes.map((o, i) => {
          const pct = d.total_votos ? Math.round((o.votos / d.total_votos) * 100) : 0;
          const minha = d.minha_opcao === i;
          const vencedora = d.vencedora === i;
          const mostraResultado = d.ja_votei || d.encerrada;
          return (
            <li key={i}>
              <button
                onClick={() => votar(i)}
                disabled={ocupado || d.ja_votei || !aberta}
                className={`relative w-full overflow-hidden rounded border px-3 py-2 text-left text-sm disabled:cursor-default ${
                  vencedora ? "border-amber-400" : "border-zinc-300"
                }`}
              >
                {mostraResultado && (
                  <span
                    aria-hidden="true"
                    className={`absolute inset-y-0 left-0 ${vencedora ? "bg-amber-200" : "bg-zinc-100"}`}
                    style={{ width: `${pct}%` }}
                  />
                )}
                <span className="relative flex items-center gap-2">
                  <span>{o.texto}</span>
                  {minha && <span className="rounded bg-zinc-900 px-1.5 text-xs text-white">seu voto</span>}
                  {mostraResultado && (
                    <span className="ml-auto tabular-nums text-zinc-600">
                      {pct}% · {o.votos}
                    </span>
                  )}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
      <p className="text-xs text-zinc-500">
        {d.total_votos} {d.total_votos === 1 ? "voto" : "votos"} ·{" "}
        {d.encerrada || !aberta
          ? d.vencedora === null && d.encerrada
            ? "votação encerrada sem votos"
            : "votação encerrada"
          : `termina em ${restante(d.prazo, agora)}`}
      </p>
      {erro && <p className="text-sm text-red-700">{erro}</p>}
    </section>
  );
}
