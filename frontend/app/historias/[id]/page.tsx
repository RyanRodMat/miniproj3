"use client";

import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { BlocoVotacao } from "@/components/BlocoVotacao";
import { MapaJornada } from "@/components/MapaJornada";
import { ApiError, apiGet, type Jornada } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

export default function HistoriaPage() {
  useExigeLogin();
  const { id } = useParams<{ id: string }>();
  const [jornada, setJornada] = useState<Jornada | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  const carregar = useCallback(() => {
    if (!localStorage.getItem("token")) return;
    apiGet<Jornada>(`/historias/${id}/jornada`)
      .then(setJornada)
      .catch((e) =>
        setErro(e instanceof ApiError && e.status === 404 ? "história não encontrada" : "erro ao carregar")
      );
  }, [id]);

  useEffect(carregar, [carregar]);

  // a decisão em aberto é a do último capítulo do caminho
  const ultimo = jornada?.caminho.at(-1);
  const emVotacao = ultimo?.decisao && !ultimo.decisao.encerrada ? ultimo.decisao : null;

  return (
    <div className="space-y-6">
      {erro && <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</p>}
      {jornada && (
        <>
          <h1 className="text-xl font-semibold">{jornada.titulo}</h1>
          {emVotacao && <BlocoVotacao decisaoId={emVotacao.id} aoEncerrar={carregar} />}
          <section className="space-y-2">
            <h2 className="text-sm font-medium text-zinc-600">Mapa da jornada</h2>
            <MapaJornada jornada={jornada} />
          </section>
        </>
      )}
    </div>
  );
}
