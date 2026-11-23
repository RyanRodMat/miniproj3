"use client";

import { NovoPost } from "@/components/NovoPost";
import { useExigeLogin } from "@/lib/useExigeLogin";

export default function Home() {
  useExigeLogin();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Feed</h1>
      <NovoPost />
      <p className="text-zinc-600">
        O feed dos seguidos (feature do núcleo) ainda vai aparecer aqui. Enquanto
        isso, cada post tem sua página em <code>/posts/&lt;id&gt;</code>.
      </p>
    </div>
  );
}
