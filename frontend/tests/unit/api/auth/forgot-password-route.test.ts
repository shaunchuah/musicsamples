// frontend/tests/unit/api/auth/forgot-password-route.test.ts
// Validates the /api/auth/forgot-password route handler's payload parsing and backend error propagation.
// Exists to ensure the password reset request proxy rejects malformed submissions and reflects backend failures.

import { beforeEach, describe, expect, it, vi } from "vitest";

import { POST } from "@/app/api/auth/forgot-password/route";

const fetchMock = vi.fn<typeof fetch>();

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: init.status ?? 200,
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
  });
}

describe("/api/auth/forgot-password POST", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    globalThis.fetch = fetchMock;
  });

  it("rejects invalid JSON bodies", async () => {
    const request = new Request("http://localhost/api/auth/forgot-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{bad",
    });

    const response = await POST(request);

    expect(response.status).toBe(400);
    expect(await response.json()).toEqual({ error: "Invalid request body." });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("returns backend failure messages when the reset email cannot be sent", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ error: "Too many attempts." }, { status: 429 }));

    const request = new Request("http://localhost/api/auth/forgot-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "user@example.com" }),
    });

    const response = await POST(request);

    expect(response.status).toBe(429);
    expect(await response.json()).toEqual({ error: "Too many attempts." });
  });

  it("proxies successful reset requests when the backend accepts them", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ success: true }));

    const request = new Request("http://localhost/api/auth/forgot-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "user@example.com" }),
    });

    const response = await POST(request);

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ success: true });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/password-reset\/$/),
      expect.objectContaining({ method: "POST" }),
    );
  });
});
