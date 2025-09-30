// frontend/tests/unit/api/auth/reset-password-route.test.ts
// Covers the /api/auth/reset-password route handler to confirm it validates payloads and forwards backend responses.
// Exists to guarantee the reset confirmation proxy accepts only complete submissions and surfaces backend errors clearly.

import { beforeEach, describe, expect, it, vi } from "vitest";

import { POST } from "@/app/api/auth/reset-password/route";

const fetchMock = vi.fn<typeof fetch>();

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: init.status ?? 200,
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
  });
}

describe("/api/auth/reset-password POST", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    globalThis.fetch = fetchMock;
  });

  it("requires uid, token, and newPassword fields", async () => {
    const request = new Request("http://localhost/api/auth/reset-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ uid: "uid" }),
    });

    const response = await POST(request);

    expect(response.status).toBe(400);
    expect(await response.json()).toEqual({ error: "All fields are required." });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("returns backend error messages when reset confirmation fails", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ error: "Token expired." }, { status: 400 }));

    const request = new Request("http://localhost/api/auth/reset-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ uid: "uid", token: "badtoken", newPassword: "password123" }),
    });

    const response = await POST(request);

    expect(response.status).toBe(400);
    expect(await response.json()).toEqual({ error: "Token expired." });
  });

  it("returns success when the backend confirms the reset", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ success: true }));

    const request = new Request("http://localhost/api/auth/reset-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ uid: "uid", token: "token", newPassword: "password123" }),
    });

    const response = await POST(request);

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ success: true });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/password-reset\/confirm\/$/),
      expect.objectContaining({ method: "POST" }),
    );
  });
});
