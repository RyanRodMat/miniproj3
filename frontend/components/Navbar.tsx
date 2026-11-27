"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import NavAuth from "@/components/NavAuth";

/**
 * Mesma grade do corpo da página (layout.tsx): com login, o espaço da barra lateral
 * "Seguindo" é reservado à esquerda, para o conteúdo da navbar ficar alinhado com o feed.
 */
export default function Navbar() {
  const pathname = usePathname();
  const [logado, setLogado] = useState(false);

  useEffect(() => {
    setLogado(!!localStorage.getItem("token"));
  }, [pathname]);

  return (
    <nav className="border-b border-zinc-200 bg-white">
      <div className="mx-auto flex max-w-5xl gap-6 px-4 py-3">
        {logado && <div className="hidden w-56 shrink-0 lg:block" />}
        <div className="mx-auto flex min-w-0 max-w-3xl flex-1 items-center gap-6">
          <Link href="/" className="flex items-center gap-2 text-xl font-bold text-zinc-900">
            <Image src="/marte-logo.png" alt="" width={215} height={94} className="h-8 w-auto" priority />
            Marte
          </Link>
          <Link href="/explorar" className="text-sm text-zinc-600 hover:text-zinc-900">
            Explorar
          </Link>
          <Link href="/foruns" className="text-sm text-zinc-600 hover:text-zinc-900">
            Fóruns
          </Link>
          <Link href="/usuarios" className="text-sm text-zinc-600 hover:text-zinc-900">
            Usuários
          </Link>
          <div className="ml-auto">
            <NavAuth />
          </div>
        </div>
      </div>
    </nav>
  );
}
