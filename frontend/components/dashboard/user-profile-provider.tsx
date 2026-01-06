// frontend/components/dashboard/user-profile-provider.tsx
// Stores the authenticated user's profile data in a global client context with session persistence.
// Exists to avoid refetching permissions on every navigation click while keeping logout cleanup simple.

"use client";

import type { ReactNode } from "react";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { DashboardUser } from "@/types/dashboard";

type DashboardUserContextValue = {
  user: DashboardUser | null;
  setUser: (next: DashboardUser | null) => void;
  refreshUser: () => Promise<void>;
};

type UserProfileResponse = {
  email?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  is_staff?: boolean;
  is_superuser?: boolean;
  groups?: unknown;
};

const STORAGE_KEY = "dashboard-user-profile";

const DashboardUserContext = createContext<DashboardUserContextValue | undefined>(undefined);

function normaliseGroups(groups: unknown): string[] {
  if (Array.isArray(groups)) {
    return groups.filter((value): value is string => typeof value === "string");
  }
  return [];
}

function normaliseUserProfile(payload: UserProfileResponse): DashboardUser {
  return {
    email: typeof payload.email === "string" ? payload.email : null,
    firstName: typeof payload.first_name === "string" ? payload.first_name : null,
    lastName: typeof payload.last_name === "string" ? payload.last_name : null,
    isStaff: Boolean(payload.is_staff),
    isSuperuser: Boolean(payload.is_superuser),
    groups: normaliseGroups(payload.groups),
  };
}

function readStoredUser(): DashboardUser | null {
  if (typeof window === "undefined") {
    return null;
  }

  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw) as DashboardUser;
    if (!parsed || typeof parsed !== "object") {
      return null;
    }
    return {
      email: typeof parsed.email === "string" ? parsed.email : null,
      firstName: typeof parsed.firstName === "string" ? parsed.firstName : null,
      lastName: typeof parsed.lastName === "string" ? parsed.lastName : null,
      isStaff: Boolean(parsed.isStaff),
      isSuperuser: Boolean(parsed.isSuperuser),
      groups: Array.isArray(parsed.groups)
        ? parsed.groups.filter((value): value is string => typeof value === "string")
        : [],
      accessLevel: parsed.accessLevel,
    };
  } catch {
    return null;
  }
}

function persistUser(next: DashboardUser | null) {
  if (typeof window === "undefined") {
    return;
  }

  if (!next) {
    localStorage.removeItem(STORAGE_KEY);
    return;
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
}

export function DashboardUserProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<DashboardUser | null>(() => readStoredUser());

  const setUser = useCallback((next: DashboardUser | null) => {
    setUserState(next);
    persistUser(next);
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const response = await fetch("/api/dashboard/user", { cache: "no-store" });
      if (!response.ok) {
        return;
      }
      const payload = (await response.json()) as UserProfileResponse;
      const normalised = normaliseUserProfile(payload);
      setUserState((current) => {
        const combined: DashboardUser = {
          ...(current ?? {}),
          ...normalised,
          groups: normalised.groups ?? current?.groups ?? [],
        };
        persistUser(combined);
        return combined;
      });
    } catch {
      // Ignore fetch failures and retain cached profile data.
    }
  }, []);

  useEffect(() => {
    if (!user) {
      const stored = readStoredUser();
      if (stored) {
        setUserState(stored);
      }
    }
  }, [user]);

  useEffect(() => {
    void refreshUser();
  }, [refreshUser]);

  const value = useMemo<DashboardUserContextValue>(
    () => ({
      user,
      setUser,
      refreshUser,
    }),
    [refreshUser, setUser, user],
  );

  return <DashboardUserContext.Provider value={value}>{children}</DashboardUserContext.Provider>;
}

export function useDashboardUser(): DashboardUserContextValue {
  const context = useContext(DashboardUserContext);
  if (!context) {
    throw new Error("useDashboardUser must be used within DashboardUserProvider");
  }
  return context;
}
