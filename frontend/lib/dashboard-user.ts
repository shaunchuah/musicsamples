// frontend/lib/dashboard-user.ts
// Provides a shared helper for resolving dashboard user info from JWT payloads.
// Exists to avoid duplicating token parsing logic across multiple dashboard pages.

import { parseJwt } from "@/lib/jwt";
import type { DashboardUser } from "@/types/dashboard";

export function resolveDashboardUser(token: string | null | undefined): DashboardUser {
  if (!token) {
    return { email: null, firstName: null, lastName: null };
  }

  const payload = parseJwt(token);
  if (!payload || typeof payload !== "object") {
    return { email: null, firstName: null, lastName: null };
  }

  const email = (() => {
    const value = payload?.email ?? payload?.user_email ?? null;
    return typeof value === "string" ? value : null;
  })();

  const firstName = (() => {
    const value = payload?.first_name ?? payload?.firstName ?? null;
    return typeof value === "string" ? value : null;
  })();

  const lastName = (() => {
    const value = payload?.last_name ?? payload?.lastName ?? null;
    return typeof value === "string" ? value : null;
  })();

  return { email, firstName, lastName };
}
