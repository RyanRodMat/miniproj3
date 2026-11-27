"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { MarcaMarte } from "@/components/MarcaMarte";
import { apiPost } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function entrar(e: React.FormEvent) {
    e.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      const { token } = await apiPost<{ token: string }>("/auth/login", {
        username,
        password,
      });
      localStorage.setItem("token", token);
      router.push("/");
    } catch {
      setErro("Usuário ou senha inválidos.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-sm">
      <MarcaMarte />
      <h1 className="mb-6 text-2xl font-semibold">Entrar</h1>

      <form onSubmit={entrar} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          Usuário
          <input
            className="rounded border px-3 py-2"
            value={username}
            onChange={(e) => setUsername(e.target.value.toLowerCase())}
            autoComplete="username"
            required
          />
        </label>

        <label className="flex flex-col gap-1 text-sm">
          Senha
          <input
            type="password"
            className="rounded border px-3 py-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>

        {erro && (
          <p role="alert" className="text-sm text-red-600">
            {erro}
          </p>
        )}

        <button
          type="submit"
          disabled={enviando}
          className="rounded bg-zinc-900 px-4 py-2 text-white disabled:opacity-50"
        >
          {enviando ? "Entrando..." : "Entrar"}
        </button>
      </form>

      <p className="mt-6 text-sm">
        Ainda não tem conta?{" "}
        <Link href="/registro" className="underline">
          Criar conta
        </Link>
      </p>
    </div>
  );
}
