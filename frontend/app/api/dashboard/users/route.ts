// frontend/app/api/dashboard/users/route.ts
// Provides a server-side proxy for listing and creating users via the Django api_v3 endpoints.
// Exists so the Next.js client can manage staff users without exposing HTTP-only auth tokens.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const USERS_ENDPOINT = "/api/v3/users/";
const USER_EMAILS_ENDPOINT = "/api/v3/management/user-emails/";

type JsonLike = Record<string, unknown> | null;

async function readJsonSafely(response: Response): Promise<JsonLike> {
  try {
    return (await response.json()) as JsonLike;
  } catch {
    return null;
  }
}

function unauthorizedResponse() {
  return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
}

export async function GET(request: Request) {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return unauthorizedResponse();
  }

  const incomingUrl = new URL(request.url);
  const path = incomingUrl.searchParams.get("variant");

  // If the client asks for management emails, proxy the dedicated endpoint.
  if (path === "emails") {
    try {
      const response = await fetch(buildBackendUrl(USER_EMAILS_ENDPOINT), {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        cache: "no-store",
      });

      const payload = await readJsonSafely(response);

      if (!response.ok) {
        return NextResponse.json(
          { detail: payload?.detail ?? payload?.error ?? "Failed to fetch user emails" },
          { status: response.status },
        );
      }

      return NextResponse.json(payload);
    } catch (error) {
      console.error("Failed to fetch user emails:", error);
      return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
    }
  }

  try {
    const backendUrl = new URL(buildBackendUrl(USERS_ENDPOINT));
    incomingUrl.searchParams.forEach((value, key) => {
      backendUrl.searchParams.set(key, value);
    });

    const response = await fetch(backendUrl, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    const payload = await readJsonSafely(response);

    if (!response.ok) {
      return NextResponse.json(
        { detail: payload?.detail ?? payload?.error ?? "Failed to fetch users" },
        { status: response.status },
      );
    }

    return NextResponse.json(payload);
  } catch (error) {
    console.error("Failed to fetch users:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}

export async function POST(request: Request) {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return unauthorizedResponse();
  }

  let body: unknown;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid JSON payload" }, { status: 400 });
  }

  try {
    const response = await fetch(buildBackendUrl(USERS_ENDPOINT), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      cache: "no-store",
    });

    const payload = await readJsonSafely(response);

    if (!response.ok) {
      return NextResponse.json(
        { detail: payload?.detail ?? payload?.error ?? "Unable to create user" },
        { status: response.status },
      );
    }

    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    console.error("Failed to create user:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
// frontend/app/api/dashboard/users/route.ts
// Provides a server-side proxy for listing and creating users via the Django api_v3 endpoints.
// Exists so the Next.js client can manage staff users without exposing HTTP-only auth tokens.
