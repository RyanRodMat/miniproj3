import Link from "next/link";

// mesma regra do backend (core/tags.py): #tag com [A-Za-z0-9_], sem colar em outra palavra
const HASHTAG = /(?<![\w#&])#([A-Za-z0-9_]+)(?![\wÀ-ÿ])/g;

/** Texto do post com cada `#tag` virando link para o Explorar filtrado. */
export function TextoComTags({ texto }: { texto: string }) {
  const partes: React.ReactNode[] = [];
  let ultimo = 0;
  for (const m of texto.matchAll(HASHTAG)) {
    const inicio = m.index ?? 0;
    partes.push(texto.slice(ultimo, inicio));
    partes.push(
      <Link
        key={inicio}
        href={`/explorar?tag=${m[1].toLowerCase()}`}
        className="font-medium text-zinc-700 hover:underline"
      >
        #{m[1]}
      </Link>,
    );
    ultimo = inicio + m[0].length;
  }
  partes.push(texto.slice(ultimo));
  return <>{partes}</>;
}
