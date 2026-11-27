"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { BlocoVotacao } from "@/components/BlocoVotacao";
import { MapaJornada } from "@/components/MapaJornada";
import { ApiError, apiGet, type Historia, type Jornada } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

export default function HistoriaPage() {
  useExigeLogin();
  const { id } = useParams<{ id: string }>();
  const [historia, setHistoria] = useState<Historia | null>(null);
  const [jornada, setJornada] = useState<Jornada | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  const carregarJornada = useCallback(() => {
    apiGet<Jornada>(`/historias/${id}/jornada`).then(setJornada).catch(() => {});
  }, [id]);

  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    apiGet<Historia>(`/historias/${id}`)
      .then(setHistoria)
      .catch((e) =>
        setErro(e instanceof ApiError && e.status === 404 ? "história não encontrada" : "erro ao carregar a história")
      );
    carregarJornada();
  }, [id, carregarJornada]);

  if (erro) return <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</p>;
  if (!historia) return null;

  // a decisão em aberto é a do último capítulo do caminho
  const ultimo = jornada?.caminho.at(-1);
  const emVotacao = ultimo?.decisao && !ultimo.decisao.encerrada ? ultimo.decisao : null;

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-4 sm:flex-row">
        {historia.capa_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={historia.capa_url} alt={`capa de ${historia.titulo}`} className="w-48 rounded border object-cover" />
        )}
        <div className="space-y-2">
          <h1 className="text-2xl font-bold">{historia.titulo}</h1>
          <Link href={`/u/${historia.autor.username}`} className="text-sm text-zinc-600 hover:underline">
            por {historia.autor.name} (@{historia.autor.username})
          </Link>
          <p className="whitespace-pre-wrap">{historia.sinopse}</p>
          <ul className="flex flex-wrap gap-1.5">
            {historia.tags.map((t) => (
              <li key={t} className="rounded bg-zinc-100 px-1.5 py-0.5 text-xs text-zinc-600">
                #{t}
              </li>
            ))}
          </ul>
        </div>
      </header>

      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Capítulos</h2>
        {historia.capitulos.length === 0 && <p className="text-zinc-500">Ainda não há capítulos publicados.</p>}
        <ol className="space-y-2">
          {historia.capitulos.map((c) => (
            <li key={c.id}>
              <Link
                href={`/historias/${historia.id}/capitulos/${c.numero}`}
                className="block rounded-lg border bg-white p-3 hover:bg-zinc-50"
              >
                <span className="text-zinc-500">Capítulo {c.numero}</span> · {c.titulo}
              </Link>
            </li>
          ))}
        </ol>
      </section>

      {emVotacao && <BlocoVotacao decisaoId={emVotacao.id} aoEncerrar={carregarJornada} />}

      {jornada && jornada.caminho.length > 0 && (
        <section className="space-y-2">
          <h2 className="text-sm font-medium text-zinc-600">Mapa da jornada</h2>
          <MapaJornada jornada={jornada} />
        </section>
      )}
    </div>
  );
}
