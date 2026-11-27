"use client";

import { useState, type ReactNode } from "react";

import { Comentarios } from "@/components/Comentarios";

/**
 * Botão "comentários" que abre a lista (e o campo para comentar) dentro do próprio post.
 * `children` (o botão de curtir) fica na mesma linha do botão.
 */
export function ComentariosDoPost({ postId, children }: { postId: number; children?: ReactNode }) {
  const [aberto, setAberto] = useState(false);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-start gap-2">
        {children}
        <button
          onClick={() => setAberto((a) => !a)}
          aria-expanded={aberto}
          className="rounded border border-zinc-300 bg-white px-3 py-1 text-sm text-zinc-600 hover:bg-zinc-100"
        >
          {aberto ? "ocultar comentários" : "comentários"}
        </button>
      </div>
      {aberto && <Comentarios alvo="posts" id={postId} />}
    </div>
  );
}
