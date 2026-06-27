import { apiFetch } from "./api";
import { getRefreshToken } from "./tokens";

export type TokenPair = { access: string; refresh: string };

/** POST /token/ — exchange email + password for a JWT pair. */
export function loginRequest(email: string, password: string): Promise<TokenPair> {
  return apiFetch<TokenPair>("/token/", {
    method: "POST",
    auth: false,
    body: { email, password },
  });
}

/** POST /register — create a new account. */
export function registerRequest(email: string, password: string): Promise<{ email: string }> {
  return apiFetch<{ email: string }>("/register", {
    method: "POST",
    auth: false,
    body: { email, password },
  });
}

/** POST /logout/ — best-effort blacklist of the refresh token. */
export async function logoutRequest(): Promise<void> {
  const refresh = getRefreshToken();
  if (!refresh) return;
  try {
    await apiFetch("/logout/", { method: "POST", body: { refresh } });
  } catch {
    // Server-side blacklist may be unavailable; clearing local tokens is
    // what actually signs the user out, so this failure is non-fatal.
  }
}
