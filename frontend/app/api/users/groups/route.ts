// frontend/app/api/users/groups/route.ts
// Proxies the available Django auth group names for use in the user management UI.
// Exists to let the Next.js dashboard fetch group options without exposing JWT cookies to the browser.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const GROUPS_ENDPOINT = "/api/v3/users/groups/";

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

export async function GET() {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return unauthorizedResponse();
  }

  try {
    const response = await fetch(buildBackendUrl(GROUPS_ENDPOINT), {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    const payload = await readJsonSafely(response);

    if (!response.ok) {
      return NextResponse.json(
        { detail: payload?.detail ?? payload?.error ?? "Failed to fetch groups" },
        { status: response.status },
      );
    }

    return NextResponse.json(payload);
  } catch (error) {
    console.error("Failed to fetch groups:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
