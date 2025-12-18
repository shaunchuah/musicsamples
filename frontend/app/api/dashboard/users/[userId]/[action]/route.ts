// frontend/app/api/dashboard/users/[userId]/[action]/route.ts
// Proxies staff-only user actions (make/remove staff, activate/deactivate) to the Django api_v3 backend.
// Exists to keep privileged JWTs server-side while the Next.js UI triggers management mutations.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const USERS_ENDPOINT = "/api/v3/users/";
const ALLOWED_ACTIONS = new Set(["make_staff", "remove_staff", "activate", "deactivate"]);

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

export async function POST(
  _request: Request,
  context: RouteContext<"/api/dashboard/users/[userId]/[action]">,
) {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return unauthorizedResponse();
  }

  const params = await context.params;
  const userId = params.userId;
  const action = params.action;

  if (!userId) {
    return NextResponse.json({ detail: "User id is required" }, { status: 400 });
  }

  if (!action || !ALLOWED_ACTIONS.has(action)) {
    return NextResponse.json({ detail: "Unsupported action" }, { status: 400 });
  }

  try {
    const response = await fetch(
      buildBackendUrl(`${USERS_ENDPOINT}${encodeURIComponent(userId)}/${action}/`),
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
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
// frontend/app/api/dashboard/users/[userId]/[action]/route.ts
// Proxies staff-only user actions (make/remove staff, activate/deactivate) to the Django api_v3 backend.
// Exists to keep privileged JWTs server-side while the Next.js UI triggers management mutations.
