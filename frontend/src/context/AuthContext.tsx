import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { toast } from "sonner";

import { loginRequest, logoutRequest, registerRequest } from "@/lib/auth";
import { onSessionExpired } from "@/lib/session";
import {
  clearAuth,
  getAccessToken,
  getStoredEmail,
  setStoredEmail,
  setTokens,
} from "@/lib/tokens";

type User = { email: string };

type AuthContextValue = {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Restore session from stored tokens on first load.
  useEffect(() => {
    const token = getAccessToken();
    const email = getStoredEmail();
    if (token && email) setUser({ email });
    setLoading(false);
  }, []);

  // When the API layer reports an unrecoverable 401, drop the session. With
  // `user` cleared, ProtectedRoute redirects to /login.
  useEffect(() => {
    return onSessionExpired(() => {
      clearAuth();
      setUser((current) => {
        if (current) {
          toast.error("Session expired", {
            id: "session-expired",
            description: "Please sign in again.",
          });
        }
        return null;
      });
    });
  }, []);

  async function login(email: string, password: string) {
    const tokens = await loginRequest(email, password);
    setTokens(tokens.access, tokens.refresh);
    setStoredEmail(email);
    setUser({ email });
  }

  async function register(email: string, password: string) {
    await registerRequest(email, password);
    // Account created — sign straight in.
    await login(email, password);
  }

  async function logout() {
    await logoutRequest();
    clearAuth();
    setUser(null);
  }

  const value = useMemo<AuthContextValue>(
    () => ({ user, isAuthenticated: user !== null, loading, login, register, logout }),
    [user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
