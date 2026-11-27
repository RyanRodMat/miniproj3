"use client";

import { Comentarios } from "@/components/Comentarios";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { ApiError, apiGet, apiUrl, type Capitulo, type Historia } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

/** Leitor: páginas em sequência, rolagem vertical, sem espaço entre elas. */
export default function CapituloPage() {
  useExigeLogin();
  const { id, numero } = useParams<{ id: string; numero: string }>();
  const [capitulo, setCapitulo] = useState<Capitulo | null>(null);
  const [historia, setHistoria] = useState<Historia | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    setCapitulo(null);
    apiGet<Capitulo>(`/historias/${id}/capitulos/${numero}`)
      .then((c) => {
        setCapitulo(c);
        setErro(null);
      })
      .catch((e) =>
        setErro(e instanceof ApiError && e.status === 404 ? "capítulo não encontrado" : "erro ao carregar o capítulo")
      );
    apiGet<Historia>(`/historias/${id}`).then(setHistoria).catch(() => {});
  }, [id, numero]);

  if (erro) return <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</p>;
  if (!capitulo) return null;

  const atual = capitulo.numero;
  const anterior = historia?.capitulos.find((c) => c.numero === atual - 1);
  const proximo = historia?.capitulos.find((c) => c.numero === atual + 1);

  const navegacao = (
    <nav className="flex justify-between text-sm">
      {anterior ? (
        <Link href={`/historias/${id}/capitulos/${anterior.numero}`} className="text-zinc-600 hover:underline">
          ← capítulo {anterior.numero}
        </Link>
      ) : (
        <span />
      )}
      {proximo && (
        <Link href={`/historias/${id}/capitulos/${proximo.numero}`} className="text-zinc-600 hover:underline">
          capítulo {proximo.numero} →
        </Link>
      )}
    </nav>
  );

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <header>
        <Link href={`/historias/${id}`} className="text-sm text-zinc-500 hover:underline">
          ← {historia?.titulo ?? "história"}
        </Link>
        <h1 className="text-xl font-bold">
          Capítulo {atual}: {capitulo.titulo}
        </h1>
      </header>
      {navegacao}
      <div className="flex flex-col">
        {capitulo.paginas.map((url, i) => (
        // eslint-disable-next-line @next/next/no-img-element
          <img
            key={url + i}
            src={apiUrl(url)}
            alt={`página ${i + 1}`}
            className="w-full"
            loading="lazy"
          />
        ))}
      </div>
      {capitulo.texto && <p className="whitespace-pre-wrap">{capitulo.texto}</p>}
      {navegacao}
      <Comentarios key={capitulo.id} alvo="capitulos" id={capitulo.id} />
    </div>
  );
}
