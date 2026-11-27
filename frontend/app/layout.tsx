import type { Metadata } from "next";
import { Urbanist } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import SidebarSeguindo from "@/components/SidebarSeguindo";

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
        <Navbar />
        <div className="mx-auto flex max-w-5xl gap-6 px-4 py-6">
          <SidebarSeguindo />
          <main className="mx-auto min-w-0 max-w-3xl flex-1">{children}</main>
        </div>
      </body>
    </html>
  );
}
