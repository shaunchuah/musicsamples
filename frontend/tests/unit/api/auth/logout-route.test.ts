// frontend/tests/unit/api/auth/logout-route.test.ts
// Ensures the /api/auth/logout route handler clears cookies and notifies the backend when possible.
// Exists to verify the logout proxy invalidates tokens locally even if backend revocation is skipped or fails.

import { beforeEach, describe, expect, it, vi } from "vitest";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, REFRESH_COOKIE_NAME } from "@/lib/auth";

const fetchMock = vi.fn<typeof fetch>();
const { cookiesMock } = vi.hoisted(() => ({
  cookiesMock: vi.fn(),
})) as { cookiesMock: ReturnType<typeof vi.fn> };

vi.mock("next/headers", () => ({
  cookies: cookiesMock,
}));

import { POST } from "@/app/api/auth/logout/route";

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: init.status ?? 200,
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
  });
}

describe("/api/auth/logout POST", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    cookiesMock.mockReset();
    globalThis.fetch = fetchMock;
  });

  it("clears cookies even when no refresh token is present", async () => {
    cookiesMock.mockResolvedValue({
      get: () => undefined,
    });

    const response = (await POST()) as NextResponse;

    expect(fetchMock).not.toHaveBeenCalled();
    expect(response.status).toBe(200);

    const authCookie = response.cookies.get(AUTH_COOKIE_NAME);
    const refreshCookie = response.cookies.get(REFRESH_COOKIE_NAME);

    expect(authCookie?.value).toBe("");
    expect(authCookie?.maxAge).toBe(0);
    expect(refreshCookie?.value).toBe("");
    expect(refreshCookie?.maxAge).toBe(0);
  });

  it("attempts backend revocation and clears cookies when a refresh token exists", async () => {
    cookiesMock.mockResolvedValue({
      get: () => ({ value: "refresh-token" }),
    });

    fetchMock.mockResolvedValue(jsonResponse({ success: true }));

    const response = (await POST()) as NextResponse;

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/token\/blacklist\/$/),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ refresh: "refresh-token" }),
      }),
    );

    const authCookie = response.cookies.get(AUTH_COOKIE_NAME);
    const refreshCookie = response.cookies.get(REFRESH_COOKIE_NAME);

    expect(authCookie?.value).toBe("");
    expect(authCookie?.maxAge).toBe(0);
    expect(refreshCookie?.value).toBe("");
    expect(refreshCookie?.maxAge).toBe(0);
  });
});
