// frontend/app/api/dashboard/users/[userId]/route.ts
// Proxies user detail updates to the Django api_v3 users endpoint while keeping auth tokens server-side.
// Exists so staff can edit user profiles from the Next.js app without exposing JWTs to the browser.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const USERS_ENDPOINT = "/api/v3/users/";

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

export async function PATCH(
  request: Request,
  context: RouteContext<"/api/dashboard/users/[userId]">,
) {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return unauthorizedResponse();
  }

  const params = await context.params;
  const userId = params.userId;

  if (!userId) {
    return NextResponse.json({ detail: "User id is required" }, { status: 400 });
  }

  let body: unknown;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid JSON payload" }, { status: 400 });
  }

  try {
    const response = await fetch(
      buildBackendUrl(`${USERS_ENDPOINT}${encodeURIComponent(userId)}/`),
      {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
        cache: "no-store",
      },
    );

    const payload = await readJsonSafely(response);

    if (!response.ok) {
      return NextResponse.json(
        { detail: payload?.detail ?? payload?.error ?? "Unable to update user" },
        { status: response.status },
      );
    }

    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    console.error("Failed to update user:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
// frontend/app/api/dashboard/users/[userId]/route.ts
// Proxies user detail updates to the Django api_v3 users endpoint while keeping auth tokens server-side.
// Exists so staff can edit user profiles from the Next.js app without exposing JWTs to the browser.
