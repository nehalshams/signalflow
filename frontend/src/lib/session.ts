// Tiny bridge so the non-React API layer can notify the app when the session
// becomes unrecoverable (refresh failed / token revoked) and the user must be
// signed out.

type Listener = () => void;

const listeners = new Set<Listener>();

export function onSessionExpired(fn: Listener): () => void {
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
  };
}

export function emitSessionExpired(): void {
  listeners.forEach((fn) => fn());
}
