"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { BotaoSeguir } from "@/components/BotaoSeguir";
import { ApiError, apiGet, apiPatch, type Perfil, type User } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

export default function PerfilPage() {
  useExigeLogin();
  const { username } = useParams<{ username: string }>();
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [eu, setEu] = useState<User | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  const [editando, setEditando] = useState(false);
  const [bio, setBio] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    apiGet<Perfil>(`/usuarios/${username}`)
      .then(setPerfil)
      .catch((e) =>
        setErro(e instanceof ApiError && e.status === 404 ? "usuário não encontrado" : "erro ao carregar o perfil")
      );
    apiGet<User>("/auth/eu").then(setEu).catch(() => {});
  }, [username]);

  async function salvar(e: React.FormEvent) {
    e.preventDefault();
    try {
      // o PATCH devolve só o usuário, sem contadores: mantém os que já temos
      const novo = await apiPatch<User>("/usuarios/eu", { bio, avatar_url: avatarUrl.trim() });
      setPerfil((atual) => (atual ? { ...atual, ...novo } : atual));
      setEditando(false);
      setErro(null);
    } catch (err) {
      setErro(err instanceof Error ? err.message : "erro ao salvar");
    }
  }

  if (!perfil) {
    return erro ? (
      <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</p>
    ) : null;
  }

  const ehMeu = eu?.id === perfil.id;

  return (
    <div className="space-y-4">
      {erro && <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</p>}
      <header className="flex gap-4 rounded-lg border bg-white p-4">
        <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-zinc-200 text-2xl font-semibold">
          {perfil.avatar_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={perfil.avatar_url} alt="" className="h-20 w-20 rounded-full object-cover" />
          ) : (
            perfil.name[0]?.toUpperCase()
          )}
        </div>
        <div className="min-w-0 space-y-1">
          <div className="flex items-center gap-2">
            <h1 className="truncate text-2xl font-bold">{perfil.name}</h1>
            {perfil.tipo === "artista" && (
              <span className="rounded bg-amber-100 px-1.5 py-0.5 text-xs text-amber-800">artista</span>
            )}
          </div>
          <p className="text-zinc-500">@{perfil.username}</p>
          {perfil.bio && <p className="whitespace-pre-wrap">{perfil.bio}</p>}
          <p className="text-sm">
            <strong>{perfil.seguidores}</strong> seguidores · <strong>{perfil.seguindo}</strong> seguindo
          </p>
          {eu && !ehMeu && (
            <BotaoSeguir
              username={perfil.username}
              seguindoInicial={perfil.eu_sigo}
              onMudou={(segue) =>
                setPerfil({ ...perfil, seguidores: perfil.seguidores + (segue ? 1 : -1), eu_sigo: segue })
              }
            />
          )}
          {ehMeu && !editando && (
            <button
              onClick={() => {
                setBio(perfil.bio);
                setAvatarUrl(perfil.avatar_url);
                setEditando(true);
              }}
              className="text-sm text-zinc-600 hover:text-zinc-900"
            >
              editar perfil
            </button>
          )}
        </div>
      </header>

      {ehMeu && editando && (
        <form onSubmit={salvar} className="space-y-2 rounded-lg border bg-white p-3">
          <label className="flex flex-col text-sm">
            bio
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              maxLength={280}
              rows={3}
              className="rounded border px-2 py-1"
            />
          </label>
          <label className="flex flex-col text-sm">
            URL do avatar
            <input
              value={avatarUrl}
              onChange={(e) => setAvatarUrl(e.target.value)}
              type="url"
              maxLength={300}
              className="rounded border px-2 py-1"
            />
          </label>
          <div className="flex gap-2 text-sm">
            <button type="submit" className="rounded bg-zinc-900 px-3 py-1.5 text-white">
              salvar
            </button>
            <button type="button" onClick={() => setEditando(false)} className="px-3 py-1.5 text-zinc-600">
              cancelar
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
