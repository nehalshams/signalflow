import { API_BASE_URL } from "./config";
import { emitSessionExpired } from "./session";
import {
  clearAuth,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
} from "./tokens";

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, message: string, data: unknown = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

type RequestOptions = {
  method?: string;
  body?: unknown;
  // when false, the Authorization header is not attached (login/register/refresh)
  auth?: boolean;
};

/** Pull a human-readable message out of a DRF error body. */
function messageFromBody(status: number, body: unknown): string {
  if (body && typeof body === "object") {
    const obj = body as Record<string, unknown>;
    if (typeof obj.detail === "string") return obj.detail;
    // field errors: { email: ["..."], password: ["..."] }
    for (const value of Object.values(obj)) {
      if (Array.isArray(value) && typeof value[0] === "string") return value[0];
      if (typeof value === "string") return value;
    }
  }
  return `Request failed (${status})`;
}

async function parseBody(res: Response): Promise<unknown> {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

// A single shared refresh attempt so concurrent 401s don't stampede.
let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refresh = getRefreshToken();
  if (!refresh) throw new ApiError(401, "Session expired. Please sign in again.");

  if (!refreshPromise) {
    refreshPromise = (async () => {
      const res = await fetch(`${API_BASE_URL}/token/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh }),
      });
      if (!res.ok) {
        clearAuth();
        throw new ApiError(401, "Session expired. Please sign in again.");
      }
      const data = (await res.json()) as { access: string };
      setAccessToken(data.access);
      return data.access;
    })().finally(() => {
      refreshPromise = null;
    });
  }

  return refreshPromise;
}

/**
 * Make a JSON API request. Attaches the bearer token by default and, on a
 * 401, transparently refreshes the access token once and retries.
 */
export async function apiFetch<T = unknown>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = "GET", body, auth = true } = options;

  const doFetch = async (token: string | null): Promise<Response> => {
    const headers: Record<string, string> = {};
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (auth && token) headers["Authorization"] = `Bearer ${token}`;

    return fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  };

  let res = await doFetch(auth ? getAccessToken() : null);

  if (res.status === 401 && auth && getRefreshToken()) {
    try {
      const newToken = await refreshAccessToken();
      res = await doFetch(newToken);
    } catch {
      // refresh failed — handled by the unrecoverable-401 check below
    }
  }

  // An authed request still unauthorized means the session can't be recovered;
  // clear it and notify the app so it can sign the user out and redirect.
  if (res.status === 401 && auth) {
    clearAuth();
    emitSessionExpired();
  }

  const data = await parseBody(res);
  if (!res.ok) {
    throw new ApiError(res.status, messageFromBody(res.status, data), data);
  }
  return data as T;
}
