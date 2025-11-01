// frontend/tests/unit/api/auth/login-route.test.ts
// Exercises the /api/auth/login route handler to validate request parsing, backend error handling, and cookie management.
// Exists to ensure the login proxy only accepts valid payloads and correctly persists tokens returned by the backend service.

import type { NextResponse } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { POST } from "@/app/api/auth/login/route";
import {
  ACCESS_TOKEN_MAX_AGE,
  AUTH_COOKIE_NAME,
  REFRESH_COOKIE_MAX_AGE,
  REFRESH_COOKIE_NAME,
} from "@/lib/auth";

const fetchMock = vi.fn<typeof fetch>();

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: init.status ?? 200,
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
  });
}

describe("/api/auth/login POST", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    globalThis.fetch = fetchMock;
  });

  it("returns 400 when the request body is not valid JSON", async () => {
    const request = new Request("http://localhost/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{not-json}",
    });

    const response = (await POST(request)) as NextResponse;
    const payload = (await response.json()) as { error: string };

    expect(response.status).toBe(400);
    expect(payload.error).toBe("Invalid request body.");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("returns 400 when email or password is missing", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ success: true }));

    const request = new Request("http://localhost/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "user@example.com" }),
    });

    const response = (await POST(request)) as NextResponse;
    const payload = (await response.json()) as { error: string };

    expect(response.status).toBe(400);
    expect(payload.error).toBe("Email and password are required.");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("bubbles up backend errors when authentication fails", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(
        {
          detail: "Authentication failed.",
        },
        { status: 401 },
      ),
    );

    const request = new Request("http://localhost/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "user@example.com", password: "badpass" }),
    });

    const response = (await POST(request)) as NextResponse;
    const payload = (await response.json()) as { error: string };

    expect(response.status).toBe(401);
    expect(payload.error).toBe("Authentication failed.");
  });

  it("stores access and refresh tokens when authentication succeeds", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ access: "access-token", refresh: "refresh-token" }));

    const request = new Request("http://localhost/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "user@example.com", password: "greatpass" }),
    });

    const response = (await POST(request)) as NextResponse;
    const payload = (await response.json()) as { success: boolean };

    expect(response.status).toBe(200);
    expect(payload.success).toBe(true);

    const accessCookie = response.cookies.get(AUTH_COOKIE_NAME);
    const refreshCookie = response.cookies.get(REFRESH_COOKIE_NAME);

    expect(accessCookie?.value).toBe("access-token");
    expect(accessCookie?.httpOnly).toBe(true);
    expect(accessCookie?.maxAge).toBe(ACCESS_TOKEN_MAX_AGE);

    expect(refreshCookie?.value).toBe("refresh-token");
    expect(refreshCookie?.httpOnly).toBe(true);
    expect(refreshCookie?.maxAge).toBe(REFRESH_COOKIE_MAX_AGE);
  });
});
