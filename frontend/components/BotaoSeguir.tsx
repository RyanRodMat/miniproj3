"use client";

import { useState } from "react";

import { EVENTO_SEGUINDO } from "@/components/SidebarSeguindo";
import { apiDelete, apiPost } from "@/lib/api";

type Props = {
  username: string;
  seguindoInicial: boolean;
  // avisa o pai para atualizar o contador de seguidores
  onMudou?: (agoraSegue: boolean) => void;
};

export function BotaoSeguir({ username, seguindoInicial, onMudou }: Props) {
  const [segue, setSegue] = useState(seguindoInicial);
  const [ocupado, setOcupado] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  async function alternar() {
    setOcupado(true);
    setErro(null);
    try {
      // 204 sem corpo: apiPost/apiDelete já tratam
      if (segue) await apiDelete(`/usuarios/${username}/follow`);
      else await apiPost(`/usuarios/${username}/follow`);
      setSegue(!segue);
      window.dispatchEvent(new Event(EVENTO_SEGUINDO));
      onMudou?.(!segue);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "erro");
    } finally {
      setOcupado(false);
    }
  }

  return (
    <div>
      <button
        onClick={alternar}
        disabled={ocupado}
        className={`rounded px-3 py-1.5 text-sm disabled:opacity-50 ${
          segue ? "border bg-white text-zinc-900" : "bg-zinc-900 text-white"
        }`}
      >
        {segue ? "seguindo" : "seguir"}
      </button>
      {erro && <p className="mt-1 text-sm text-red-700">{erro}</p>}
    </div>
  );
}
