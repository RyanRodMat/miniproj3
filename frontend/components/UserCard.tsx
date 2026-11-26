import Link from "next/link";

import { BotaoSeguir } from "@/components/BotaoSeguir";
import type { User } from "@/lib/api";

/** `seguir`: passe `seguindo` para mostrar o botão seguir/deixar de seguir. */
export function UserCard({ user, seguir }: { user: User; seguir?: { seguindo: boolean } }) {
  return (
    // o botão fica fora do Link: botão dentro de <a> é inválido e o clique navegaria
    <div className="flex items-center gap-3 rounded-lg border bg-white p-3 hover:bg-zinc-50">
      <Link href={`/u/${user.username}`} className="flex min-w-0 flex-1 items-center gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-zinc-200 font-semibold">
          {user.avatar_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={user.avatar_url} alt="" className="h-10 w-10 rounded-full object-cover" />
          ) : (
            user.name[0]?.toUpperCase()
          )}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate font-medium">{user.name}</p>
          <p className="truncate text-sm text-zinc-500">
            @{user.username}
            {user.bio ? ` — ${user.bio}` : ""}
          </p>
        </div>
      </Link>
      {seguir && <BotaoSeguir username={user.username} seguindoInicial={seguir.seguindo} />}
    </div>
  );
}
