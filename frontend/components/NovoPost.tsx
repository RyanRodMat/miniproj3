"use client";

import { useRef, useState } from "react";

import { apiPost, apiUpload, type Post } from "@/lib/api";

const TIPOS = ["image/jpeg", "image/png", "image/webp"];
const MAX_BYTES = 2 * 1024 * 1024;

export function NovoPost({ onCriado }: { onCriado: (post: Post) => void }) {
  const [texto, setTexto] = useState("");
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function escolher(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] ?? null;
    setErro(null);
    if (f && !TIPOS.includes(f.type)) {
      setErro("Use uma imagem jpg, png ou webp.");
    } else if (f && f.size > MAX_BYTES) {
      setErro("A imagem passa de 2 MB.");
    } else {
      setArquivo(f);
      return;
    }
    e.target.value = "";
    setArquivo(null);
  }

  async function publicar(e: React.FormEvent) {
    e.preventDefault();
    setEnviando(true);
    setErro(null);
    try {
      let post = await apiPost<Post>("/posts", { texto });
      if (arquivo) {
        try {
          const { imagem_url } = await apiUpload<{ imagem_url: string }>(
            `/posts/${post.id}/imagem`,
            arquivo,
          );
          post = { ...post, imagem_url };
        } catch (err) {
          const msg = err instanceof Error ? err.message : "erro no upload";
          setErro(`Post publicado, mas a imagem falhou: ${msg}`);
        }
      }
      setTexto("");
      setArquivo(null);
      if (inputRef.current) inputRef.current.value = "";
      onCriado(post);
    } catch (err) {
      setErro(err instanceof Error ? err.message : "erro ao publicar");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={publicar} className="space-y-2 rounded-lg border bg-white p-3">
      <textarea
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        placeholder="O que você está desenhando?"
        required
        maxLength={2000}
        rows={3}
        className="w-full rounded border px-2 py-1"
      />
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={escolher}
        className="w-full text-sm"
      />
      {erro && <p className="text-sm text-red-700">{erro}</p>}
      <button
        type="submit"
        disabled={enviando}
        className="rounded bg-zinc-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
      >
        {enviando ? "publicando..." : "publicar"}
      </button>
    </form>
  );
}