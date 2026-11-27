"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { apiGet, apiPatch, type TagContagem } from "@/lib/api";
import { useExigeLogin } from "@/lib/useExigeLogin";

const MAX = 10;

export default function OnboardingPage() {
  useExigeLogin();
  const router = useRouter();
  const [sugeridas, setSugeridas] = useState<string[]>([]);
  const [escolhidas, setEscolhidas] = useState<string[]>([]);
  const [nova, setNova] = useState("");
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    apiGet<{ items: TagContagem[] }>("/tags?limit=20")
      .then((r) => setSugeridas(r.items.map((t) => t.tag)))
      .catch(() => {});
  }, []);

  function alternar(tag: string) {
    setEscolhidas((atuais) =>
      atuais.includes(tag) ? atuais.filter((t) => t !== tag) : atuais.length < MAX ? [...atuais, tag] : atuais,
    );
  }

  function adicionar(e: React.FormEvent) {
    e.preventDefault();
    const tag = nova.trim().replace(/^#/, "").toLowerCase();
    if (!/^[a-z0-9_]{1,30}$/.test(tag)) {
      setErro("Use só letras sem acento, números e _.");
      return;
    }
    setErro("");
    setNova("");
    setSugeridas((atuais) => (atuais.includes(tag) ? atuais : [...atuais, tag]));
    setEscolhidas((atuais) => (atuais.includes(tag) || atuais.length >= MAX ? atuais : [...atuais, tag]));
  }

  async function salvar(tags: string[]) {
    setSalvando(true);
    try {
      if (tags.length > 0) await apiPatch("/usuarios/eu", { tags_interesse: tags });
      router.push("/explorar");
    } catch {
      setErro("Não consegui salvar suas tags. Tente de novo.");
      setSalvando(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-lg space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">O que você gosta de ler?</h1>
        <p className="text-sm text-zinc-600">
          Escolha até {MAX} tags. O Explorar mostra primeiro os posts delas. Você muda isso quando quiser.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {sugeridas.map((tag) => (
          <button
            key={tag}
            type="button"
            onClick={() => alternar(tag)}
            aria-pressed={escolhidas.includes(tag)}
            className={`rounded-full border px-3 py-1 text-sm ${
              escolhidas.includes(tag)
                ? "border-zinc-900 bg-zinc-900 text-white"
                : "border-zinc-300 bg-white hover:bg-zinc-100"
            }`}
          >
            #{tag}
          </button>
        ))}
      </div>

      <form onSubmit={adicionar} className="flex gap-2">
        <input
          className="flex-1 rounded border border-zinc-300 bg-white px-3 py-2 text-sm"
          placeholder="outra tag, ex.: fantasia"
          value={nova}
          onChange={(e) => setNova(e.target.value)}
          maxLength={31}
        />
        <button type="submit" className="rounded border bg-white px-3 py-2 text-sm hover:bg-zinc-100">
          adicionar
        </button>
      </form>

      {erro && (
        <p role="alert" className="text-sm text-red-600">
          {erro}
        </p>
      )}

      <div className="flex gap-3">
        <button
          onClick={() => salvar(escolhidas)}
          disabled={salvando || escolhidas.length === 0}
          className="rounded bg-zinc-900 px-4 py-2 text-white disabled:opacity-50"
        >
          {salvando ? "salvando..." : "Continuar"}
        </button>
        <button onClick={() => salvar([])} disabled={salvando} className="px-2 text-sm text-zinc-600 hover:underline">
          pular
        </button>
      </div>
    </div>
  );
}
