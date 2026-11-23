"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { BotaoSeguir } from "@/components/BotaoSeguir";
import { ApiError, apiGet, type Perfil, type User } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

export default function PerfilPage() {
  useExigeLogin();
  const { username } = useParams<{ username: string }>();
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [eu, setEu] = useState<User | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    apiGet<Perfil>(`/usuarios/${username}`)
      .then(setPerfil)
      .catch((e) =>
        setErro(e instanceof ApiError && e.status === 404 ? "usuário não encontrado" : "erro ao carregar o perfil")
      );
    apiGet<User>("/auth/eu").then(setEu).catch(() => {});
  }, [username]);

  if (erro) return <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</p>;
  if (!perfil) return null;

  return (
    <div className="space-y-2 rounded-lg border bg-white p-4">
      <h1 className="text-2xl font-bold">{perfil.name}</h1>
      <p className="text-zinc-500">@{perfil.username}</p>
      <p className="text-sm">
        <strong>{perfil.seguidores}</strong> seguidores · <strong>{perfil.seguindo}</strong> seguindo
      </p>
      {eu && eu.id !== perfil.id && (
        <BotaoSeguir
          username={perfil.username}
          seguindoInicial={perfil.eu_sigo}
          onMudou={(segue) =>
            setPerfil({ ...perfil, seguidores: perfil.seguidores + (segue ? 1 : -1), eu_sigo: segue })
          }
        />
      )}
    </div>
  );
}
