"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import BotaoSair from "@/components/BotaoSair";

export default function NavAuth() {
  const pathname = usePathname();
  const [logado, setLogado] = useState<boolean | null>(null);

  // Relê o token a cada troca de página, para a navbar atualizar após login/logout
  useEffect(() => {
    setLogado(!!localStorage.getItem("token"));
  }, [pathname]);

  if (logado === null) return null;

  return logado ? (
    <BotaoSair />
  ) : (
    <div className="flex gap-4 text-sm">
      <Link href="/login" className="text-zinc-600 hover:text-zinc-900">
        Entrar
      </Link>
      <Link href="/registro" className="text-zinc-600 hover:text-zinc-900">
        Criar conta
      </Link>
    </div>
  );
}
