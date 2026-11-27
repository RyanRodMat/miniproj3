import type { Metadata } from "next";
import { Urbanist } from "next/font/google";
import Image from "next/image";
import Link from "next/link";
import "./globals.css";
import NavAuth from "@/components/NavAuth";

const urbanist = Urbanist({ subsets: ["latin"], variable: "--font-urbanist", display: "swap" });

export const metadata: Metadata = {
  title: "Marte",
  description: "Marte: a rede social de quadrinhos e ilustradores independentes",
  icons: { icon: "/marte-logo.png" },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR" className={urbanist.variable}>
      <body className="min-h-screen bg-zinc-50 font-sans text-zinc-900">
        <nav className="border-b border-zinc-200 bg-white">
          <div className="mx-auto flex max-w-3xl items-center gap-6 px-4 py-3">
            <Link href="/" className="flex items-center gap-2 text-xl font-bold text-zinc-900">
              <Image src="/marte-logo.png" alt="" width={215} height={94} className="h-8 w-auto" priority />
              Marte
            </Link>
            <Link href="/explorar" className="text-sm text-zinc-600 hover:text-zinc-900">
              Explorar
            </Link>
            <Link href="/usuarios" className="text-sm text-zinc-600 hover:text-zinc-900">
              Usuários
            </Link>
            <div className="ml-auto">
              <NavAuth />
            </div>
          </div>
        </nav>
        <main className="mx-auto max-w-3xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
