"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { apiGet, type User } from "@/lib/api";

/** Evento disparado pelo BotaoSeguir para a lista se atualizar sem recarregar a página. */
export const EVENTO_SEGUINDO = "seguindo-mudou";

export default function SidebarSeguindo() {
  const pathname = usePathname();
  const [logado, setLogado] = useState(false);
  const [seguidos, setSeguidos] = useState<User[]>([]);
  const [erro, setErro] = useState(false);

  const carregar = useCallback(() => {
    if (!localStorage.getItem("token")) {
      setLogado(false);
      return;
    }
    setLogado(true);
    apiGet<User[]>("/usuarios/eu/seguindo/perfis")
      .then((lista) => {
        setSeguidos(lista);
        setErro(false);
      })
      .catch(() => setErro(true));
  }, []);

  // relê a cada troca de página (login/logout) e quando alguém é seguido/deixado de seguir
  useEffect(carregar, [carregar, pathname]);
  useEffect(() => {
    window.addEventListener(EVENTO_SEGUINDO, carregar);
    return () => window.removeEventListener(EVENTO_SEGUINDO, carregar);
  }, [carregar]);

  if (!logado) return null;

  return (
    <aside className="hidden w-56 shrink-0 lg:block">
      <div className="sticky top-6 max-h-[calc(100vh-6rem)] overflow-y-auto rounded-lg border border-zinc-200 bg-white p-3">
        <h2 className="mb-2 px-1 text-sm font-semibold text-zinc-900">
          Seguindo <span className="font-normal text-zinc-500">{seguidos.length}</span>
        </h2>
        {erro && <p className="px-1 text-xs text-red-700">não consegui carregar a lista</p>}
        {!erro && seguidos.length === 0 && (
          <p className="px-1 text-xs text-zinc-500">Você ainda não segue ninguém.</p>
        )}
        <ul className="space-y-0.5">
          {seguidos.map((u) => {
            const ativo = pathname === `/u/${u.username}`;
            return (
              <li key={u.id}>
                <Link
                  href={`/u/${u.username}`}
                  className={`flex items-center gap-2 rounded px-1 py-1.5 hover:bg-zinc-100 ${
                    ativo ? "bg-zinc-100" : ""
                  }`}
                >
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-200 text-sm font-semibold">
                    {u.avatar_url ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={u.avatar_url} alt="" className="h-8 w-8 rounded-full object-cover" />
                    ) : (
                      u.name[0]?.toUpperCase()
                    )}
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-medium">{u.name}</span>
                    <span className="block truncate text-xs text-zinc-500">@{u.username}</span>
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </aside>
  );
}
