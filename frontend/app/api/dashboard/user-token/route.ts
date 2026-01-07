// frontend/app/api/dashboard/user-token/route.ts
// Proxies DRF token management requests for the current user to the Django api_v3 backend.
// Exists to keep JWT cookies server-side while allowing the datasets UI to manage API tokens.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const USER_TOKEN_ENDPOINT = "/api/v3/users/me/token/";

type JsonPayload = Record<string, unknown> | null;

async function readJsonSafely(response: Response): Promise<JsonPayload> {
  try {
    return (await response.json()) as JsonPayload;
  } catch {
    return null;
  }
}

function unauthorizedResponse() {
  return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
}

export async function GET(): Promise<Response> {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return unauthorizedResponse();
  }

  try {
    const response = await fetch(buildBackendUrl(USER_TOKEN_ENDPOINT), {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    const payload = await readJsonSafely(response);

    if (!response.ok) {
      return NextResponse.json(
        { detail: payload?.detail ?? "Failed to fetch API token" },
        { status: response.status },
      );
    }

    return NextResponse.json(payload);
  } catch (error) {
    console.error("Failed to fetch API token:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}

export async function POST(): Promise<Response> {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return unauthorizedResponse();
  }

  try {
    const response = await fetch(buildBackendUrl(USER_TOKEN_ENDPOINT), {
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
        { detail: payload?.detail ?? "Failed to generate API token" },
        { status: response.status },
      );
    }

    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    console.error("Failed to generate API token:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}

export async function DELETE(): Promise<Response> {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return unauthorizedResponse();
  }

  try {
    const response = await fetch(buildBackendUrl(USER_TOKEN_ENDPOINT), {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    const payload = await readJsonSafely(response);

    if (!response.ok) {
      return NextResponse.json(
        { detail: payload?.detail ?? "Failed to delete API token" },
        { status: response.status },
      );
    }

    return NextResponse.json(payload ?? { success: true }, { status: response.status });
  } catch (error) {
    console.error("Failed to delete API token:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
