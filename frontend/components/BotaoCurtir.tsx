"use client";

import { useState } from "react";

import { apiDelete, apiPost } from "@/lib/api";

type Props = {
  postId: number;
  curtidasInicial: number;
  curtiuInicial: boolean;
};

export function BotaoCurtir({ postId, curtidasInicial, curtiuInicial }: Props) {
  const [curtiu, setCurtiu] = useState(curtiuInicial);
  const [curtidas, setCurtidas] = useState(curtidasInicial);
  const [ocupado, setOcupado] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  async function alternar() {
    setOcupado(true);
    setErro(null);
    try {
      // 204 sem corpo: apiPost/apiDelete já tratam
      if (curtiu) await apiDelete(`/posts/${postId}/curtir`);
      else await apiPost(`/posts/${postId}/curtir`);
      setCurtidas(curtidas + (curtiu ? -1 : 1));
      setCurtiu(!curtiu);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "erro");
    } finally {
      setOcupado(false);
    }
  }

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={alternar}
        disabled={ocupado}
        aria-pressed={curtiu}
        // borda, padding, rótulo e fonte iguais nos dois estados: só cor e ícone mudam,
        // então o botão não muda de tamanho nem empurra o que está em volta
        className={`inline-flex items-center gap-1.5 rounded border px-3 py-1 text-sm disabled:opacity-50 ${
          curtiu
            ? "border-rose-200 bg-rose-100 text-rose-700"
            : "border-zinc-300 bg-white text-zinc-600"
        }`}
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          aria-hidden="true"
          fill={curtiu ? "currentColor" : "none"}
          stroke="currentColor"
          strokeWidth="2"
          strokeLinejoin="round"
        >
          <path d="M12 21s-7.5-4.6-9.6-9.2C1 8.6 2.8 5 6.3 5c2.1 0 3.6 1.1 5.7 3.3C14.1 6.1 15.6 5 17.7 5c3.5 0 5.3 3.6 3.9 6.8C19.5 16.4 12 21 12 21z" />
        </svg>
        <span>curtir</span>
        <span className="min-w-[2ch] text-right tabular-nums">{curtidas}</span>
      </button>
      {erro && <span className="text-sm text-red-700">{erro}</span>}
    </div>
  );
}
