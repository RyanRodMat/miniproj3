"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { apiPost, type Post } from "@/lib/api";

export function NovoPost() {
  const router = useRouter();
  const [texto, setTexto] = useState("");
  const [imagemUrl, setImagemUrl] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  async function publicar(e: React.FormEvent) {
    e.preventDefault();
    setEnviando(true);
    setErro(null);
    try {
      const post = await apiPost<Post>("/posts", {
        texto,
        imagem_url: imagemUrl.trim() || null,
      });
      setTexto("");
      setImagemUrl("");
      router.push(`/posts/${post.id}`);
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
        value={imagemUrl}
        onChange={(e) => setImagemUrl(e.target.value)}
        placeholder="URL da imagem (opcional — o upload vem na issue de upload)"
        type="url"
        className="w-full rounded border px-2 py-1 text-sm"
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
