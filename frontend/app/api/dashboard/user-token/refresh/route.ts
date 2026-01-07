// frontend/app/api/dashboard/user-token/refresh/route.ts
// Proxies token refresh requests for the current user to the Django api_v3 backend.
// Exists to let the datasets UI renew API tokens without exposing JWTs to the client.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const USER_TOKEN_REFRESH_ENDPOINT = "/api/v3/users/me/token/refresh/";

type JsonPayload = Record<string, unknown> | null;

async function readJsonSafely(response: Response): Promise<JsonPayload> {
  try {
    return (await response.json()) as JsonPayload;
  } catch {
    return null;
  }
}

export async function POST(): Promise<Response> {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  try {
    const response = await fetch(buildBackendUrl(USER_TOKEN_REFRESH_ENDPOINT), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    const payload = await readJsonSafely(response);

    if (!response.ok) {
      return NextResponse.json(
        { detail: payload?.detail ?? "Failed to refresh API token" },
        { status: response.status },
      );
    }

    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    console.error("Failed to refresh API token:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
