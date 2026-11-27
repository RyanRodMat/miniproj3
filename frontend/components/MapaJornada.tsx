import type { Jornada } from "@/lib/api";

/** Caminho escolhido em destaque; as opções que não venceram ficam apagadas. */
export function MapaJornada({ jornada }: { jornada: Jornada }) {
  return (
    <ol className="space-y-3">
      {jornada.caminho.map((p, idx) => {
        const proximo = jornada.caminho[idx + 1];
        return (
          <li key={p.capitulo_id} className="space-y-2">
            <div className="rounded-lg border-2 border-amber-400 bg-amber-50 px-3 py-2">
              <span className="text-xs text-zinc-500">capítulo {p.numero}</span>
              <p className="font-medium">{p.titulo}</p>
            </div>
            {p.decisao && (
              <ul className="ml-4 space-y-1 border-l-2 border-amber-400 pl-4 text-sm">
                <li className="text-xs text-zinc-500">{p.decisao.pergunta}</li>
                {p.decisao.opcoes.map((o) => (
                  <li
                    key={o.indice}
                    className={
                      o.escolhida
                        ? "font-medium text-zinc-900"
                        : "text-zinc-400 line-through decoration-zinc-300"
                    }
                  >
                    {o.escolhida ? "→ " : "· "}
                    {o.texto} <span className="tabular-nums">({o.votos})</span>
                    {o.escolhida && !proximo && (
                      <span className="ml-2 text-xs font-normal text-zinc-500">
                        próximo capítulo em breve
                      </span>
                    )}
                  </li>
                ))}
                {!p.decisao.encerrada && <li className="text-xs text-zinc-500">votação aberta</li>}
              </ul>
            )}
          </li>
        );
      })}
    </ol>
  );
}
