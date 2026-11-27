// Fetch tipado, único ponto de contato com o backend.
// Já preparado para receber o token da auth (guia 01, Parte 2).

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function headers(semToken: boolean): HeadersInit {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token && !semToken) h["Authorization"] = `Bearer ${token}`;
  return h;
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  // login e registro não levam token: um 401 de senha errada não pode apagar a sessão
  const publica = path === "/auth/login" || path === "/auth/registro";
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: headers(publica),
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store",
  });

  // 401 com token salvo = token que não vale mais (ex.: o banco foi apagado ou o
  // servidor do deploy reiniciou). Joga o token fora e volta para o login.
  if (res.status === 401 && !publica && typeof window !== "undefined" && localStorage.getItem("token")) {
    localStorage.removeItem("token");
    if (window.location.pathname !== "/login") window.location.href = "/login";
  }

  if (!res.ok) {
    const erro = await res.json().catch(() => null);
    const detail = typeof erro?.detail === "string" ? erro.detail : null;
    throw new ApiError(res.status, detail ?? `${method} ${path} → ${res.status}`);
  }

  // 204 No Content (seguir, curtir, apagar...) não tem corpo: não há JSON para ler.
  if (res.status === 204) return undefined as T;
  return res.json();
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>("GET", path);
}

export function apiPost<T>(path: string, body?: unknown): Promise<T> {
  return request<T>("POST", path, body);
}

export function apiPatch<T>(path: string, body: unknown): Promise<T> {
  return request<T>("PATCH", path, body);
}

export function apiDelete<T = void>(path: string): Promise<T> {
  return request<T>("DELETE", path);
}

// ---- tipos do slice de exemplo (espelham backend/app/schemas/user.py) ----

export type User = {
  id: number;
  username: string;
  name: string;
  bio: string;
  avatar_url: string;
  tags_interesse?: string[];
  created_at: string;
};

export type TagContagem = { tag: string; contagem: number };

export type Page<T> = {
  items: T[];
  total: number;
  offset: number;
  limit: number;
};

// ---- Posts (espelham backend/app/schemas/post.py) ----

export type Autor = {
  id: number;
  username: string;
  name: string;
  avatar_url: string;
  tipo: "artista" | "leitor";
};

export type Post = {
  id: number;
  texto: string;
  imagem_url: string | null;
  autor: Autor;
  historia_id: number | null;
  created_at: string;
  curtidas: number;
  eu_curti: boolean;
  autor_eu_sigo: boolean;
};

// ---- Perfil e follow (espelham PerfilOut em backend/app/schemas/user.py) ----

export type Perfil = User & {
  tipo: "artista" | "leitor";
  seguidores: number;
  seguindo: number;
  eu_sigo: boolean;
};

// ---- Histórias (espelham backend/app/schemas/historia.py) ----

export type CapituloResumo = { id: number; numero: number; titulo: string };

export type Capitulo = CapituloResumo & {
  historia_id: number;
  texto: string;
  paginas: string[];
};

export type Historia = {
  id: number;
  titulo: string;
  sinopse: string;
  capa_url: string | null;
  tags: string[];
  autor: Autor;
  created_at: string;
  capitulos: CapituloResumo[];
};

// ---- Jornada (espelham backend/app/schemas/jornada.py) ----

export type Decisao = {
  id: number;
  capitulo_id: number;
  pergunta: string;
  opcoes: { texto: string; votos: number }[];
  total_votos: number;
  ja_votei: boolean;
  minha_opcao: number | null;
  encerrada: boolean;
  vencedora: number | null;
  prazo: string;
};

export type Jornada = {
  historia_id: number;
  titulo: string;
  caminho: {
    capitulo_id: number;
    numero: number;
    titulo: string;
    decisao: {
      id: number;
      pergunta: string;
      prazo: string;
      encerrada: boolean;
      opcoes: { indice: number; texto: string; votos: number; escolhida: boolean }[];
    } | null;
  }[];
};

// ---- Comentários (espelham backend/app/schemas/comentario.py) ----

export type Comentario = {
  id: number;
  post_id: number | null;
  capitulo_id: number | null;
  autor_id: number;
  autor: Autor;
  texto: string;
  criado_em: string;
};
