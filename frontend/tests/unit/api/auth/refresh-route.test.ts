// frontend/tests/unit/api/auth/refresh-route.test.ts
// Checks the /api/auth/refresh route handler covering refresh cookie lookups and backend token rotation outcomes.
// Exists to ensure the session refresh proxy enforces presence of a refresh token and persists rotated tokens correctly.

import type { NextResponse } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  ACCESS_TOKEN_MAX_AGE,
  AUTH_COOKIE_NAME,
  REFRESH_COOKIE_MAX_AGE,
  REFRESH_COOKIE_NAME,
} from "@/lib/auth";

const fetchMock = vi.fn<typeof fetch>();
const { cookiesMock } = vi.hoisted(() => ({
  cookiesMock: vi.fn(),
})) as { cookiesMock: ReturnType<typeof vi.fn> };

vi.mock("next/headers", () => ({
  cookies: cookiesMock,
}));

import { POST } from "@/app/api/auth/refresh/route";

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: init.status ?? 200,
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
  });
}

describe("/api/auth/refresh POST", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    cookiesMock.mockReset();
    globalThis.fetch = fetchMock;
  });

  it("returns 401 when the refresh cookie is missing", async () => {
    cookiesMock.mockResolvedValue({
      get: () => undefined,
    });

    const response = (await POST()) as NextResponse;

    expect(response.status).toBe(401);
    expect(await response.json()).toEqual({ error: "Refresh token missing." });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("returns backend error details when refresh fails", async () => {
    cookiesMock.mockResolvedValue({
      get: () => ({ value: "refresh-token" }),
    });

    fetchMock.mockResolvedValue(jsonResponse({ detail: "Token invalid." }, { status: 401 }));

    const response = (await POST()) as NextResponse;

    expect(response.status).toBe(401);
    expect(await response.json()).toEqual({ error: "Token invalid." });
  });

  it("stores rotated tokens on success", async () => {
    cookiesMock.mockResolvedValue({
      get: () => ({ value: "refresh-token" }),
    });

    fetchMock.mockResolvedValue(
      jsonResponse({ access: "access-token", refresh: "new-refresh-token" }),
    );

    const response = (await POST()) as NextResponse;
    const payload = (await response.json()) as { success: boolean };

    expect(response.status).toBe(200);
    expect(payload.success).toBe(true);

    const accessCookie = response.cookies.get(AUTH_COOKIE_NAME);
    const refreshCookie = response.cookies.get(REFRESH_COOKIE_NAME);

    expect(accessCookie?.value).toBe("access-token");
    expect(accessCookie?.httpOnly).toBe(true);
    expect(accessCookie?.maxAge).toBe(ACCESS_TOKEN_MAX_AGE);

    expect(refreshCookie?.value).toBe("new-refresh-token");
    expect(refreshCookie?.httpOnly).toBe(true);
    expect(refreshCookie?.maxAge).toBe(REFRESH_COOKIE_MAX_AGE);
  });
});
