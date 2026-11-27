import Image from "next/image";

/** Logo + nome da rede, para o topo das telas de entrar e criar conta. */
export function MarcaMarte() {
  return (
    <div className="mb-8 flex flex-col items-center gap-2">
      <Image src="/marte-logo.png" alt="" width={215} height={94} className="h-16 w-auto" priority />
      <span className="text-3xl font-bold text-zinc-900">Marte</span>
    </div>
  );
}
