"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

/**
 * Chame no topo de toda página privada.
 * Se não houver token salvo, manda para /login.
 * (Token que deixou de valer é tratado no lib/api.ts: 401 com token => limpa e vai para /login.)
 */
export function useExigeLogin() {
  const router = useRouter();
  useEffect(() => {
    if (!localStorage.getItem("token")) router.push("/login");
  }, [router]);
}