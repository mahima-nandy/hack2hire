import { createContext, ReactNode, useContext, useMemo, useState } from "react";
import { api, tokenStore } from "./api";

type AuthContextValue = {
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  signup: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(tokenStore.access));

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuthenticated,
      async login(username, password) {
        const tokens = await api.login({ username, password });
        tokenStore.set(tokens.access, tokens.refresh);
        setIsAuthenticated(true);
      },
      async signup(username, email, password) {
        await api.signup({ username, email, password });
        const tokens = await api.login({ username, password });
        tokenStore.set(tokens.access, tokens.refresh);
        setIsAuthenticated(true);
      },
      logout() {
        tokenStore.clear();
        setIsAuthenticated(false);
      }
    }),
    [isAuthenticated]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
