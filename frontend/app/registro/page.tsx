"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { MarcaMarte } from "@/components/MarcaMarte";
import { apiPost, ApiError } from "@/lib/api";

type Tipo = "artista" | "leitor";

const TIPOS: { valor: Tipo; titulo: string; descricao: string }[] = [
  {
    valor: "leitor",
    titulo: "Leitor",
    descricao: "Segue artistas, curte e comenta nas histórias.",
  },
  {
    valor: "artista",
    titulo: "Artista",
    descricao: "Publica quadrinhos, capítulos e posts de arte.",
  },
];

export default function RegistroPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [tipo, setTipo] = useState<Tipo>("leitor");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function registrar(e: React.FormEvent) {
    e.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      await apiPost("/auth/registro", { username, name, password, tipo });

      // já entra logado depois de criar a conta
      const { token } = await apiPost<{ token: string }>("/auth/login", {
        username,
        password,
      });
      localStorage.setItem("token", token);
      router.push("/onboarding");
    } catch (err) {
      setErro(
        err instanceof ApiError && err.status === 409
          ? "Esse nome de usuário já está em uso."
          : "Não foi possível criar a conta. Confira os campos e tente de novo.",
      );
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-sm">
      <MarcaMarte />
      <h1 className="mb-6 text-2xl font-semibold">Criar conta</h1>

      <form onSubmit={registrar} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          Nome
          <input
            className="rounded border px-3 py-2"
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={80}
            autoComplete="name"
            required
          />
        </label>

        <label className="flex flex-col gap-1 text-sm">
          Nome de usuário
          <input
            className="rounded border px-3 py-2"
            value={username}
            onChange={(e) => setUsername(e.target.value.toLowerCase())}
            minLength={3}
            maxLength={30}
            pattern="[a-z0-9_]+"
            title="Use só letras minúsculas, números e _"
            autoComplete="username"
            required
          />
          <span className="text-xs text-gray-500">
            3 a 30 caracteres: letras minúsculas, números e _
          </span>
        </label>

        <label className="flex flex-col gap-1 text-sm">
          Senha
          <input
            type="password"
            className="rounded border px-3 py-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={8}
            autoComplete="new-password"
            required
          />
          <span className="text-xs text-gray-500">Mínimo de 8 caracteres</span>
        </label>

        <fieldset className="flex flex-col gap-2">
          <legend className="mb-1 text-sm">Tipo de conta</legend>
          {TIPOS.map((t) => (
            <label
              key={t.valor}
              className={`flex cursor-pointer flex-col rounded border px-3 py-2 text-sm ${
                tipo === t.valor ? "border-zinc-900 bg-gray-50" : "border-gray-300"
              }`}
            >
              <span className="flex items-center gap-2 font-medium">
                <input
                  type="radio"
                  name="tipo"
                  value={t.valor}
                  checked={tipo === t.valor}
                  onChange={() => setTipo(t.valor)}
                />
                {t.titulo}
              </span>
              <span className="ml-6 text-gray-600">{t.descricao}</span>
            </label>
          ))}
        </fieldset>

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
          {enviando ? "Criando conta..." : "Criar conta"}
        </button>
      </form>

      <p className="mt-6 text-sm">
        Já tem conta?{" "}
        <Link href="/login" className="underline">
          Entrar
        </Link>
      </p>
    </div>
  );
}