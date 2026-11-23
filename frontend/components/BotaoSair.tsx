"use client";

import { useRouter } from "next/navigation";

export default function BotaoSair() {
  const router = useRouter();

  function sair() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  return (
    <button onClick={sair} className="text-sm text-zinc-600 hover:text-zinc-900">
      Sair
    </button>
  );
}
