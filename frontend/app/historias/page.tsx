"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { apiGet, type Historia } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

export default function HistoriasPage() {
  useExigeLogin();
  const [historias, setHistorias] = useState<Historia[] | null>(null);
  const [erro, setErro] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    apiGet<Historia[]>("/historias").then(setHistorias).catch(() => setErro(true));
  }, []);

  if (erro) return <p className="text-sm text-red-700">erro ao carregar as histórias</p>;
  if (!historias) return null;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Jornadas</h1>
      {historias.length === 0 && <p className="text-zinc-500">Ainda não há histórias.</p>}
      <ul className="space-y-3">
        {historias.map((h) => (
          <li key={h.id} className="space-y-2 rounded-lg border bg-white p-4">
            <Link href={`/historias/${h.id}`} className="text-lg font-semibold hover:underline">
              {h.titulo}
            </Link>
            <p className="text-sm text-zinc-600">
              por {h.autor.name} · {h.capitulos.length} capítulo(s)
            </p>
            <p className="text-sm">{h.sinopse}</p>
            <Link
              href={`/historias/${h.id}#jornada`}
              className="inline-block rounded border border-amber-400 bg-amber-50 px-3 py-1 text-sm text-amber-900 hover:bg-amber-100"
            >
              Ver jornada
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
