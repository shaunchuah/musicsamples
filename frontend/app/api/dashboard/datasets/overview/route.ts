// frontend/app/api/dashboard/datasets/overview/route.ts
// Proxies dataset overview requests to the Django api_v3 endpoint for the datasets dashboard.
// Exists to keep auth tokens server-side while the Next.js client consumes the overview data.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const DATASETS_OVERVIEW_ENDPOINT = "/api/v3/datasets/overview/";

type JsonPayload = Record<string, unknown> | null;

async function readJsonSafely(response: Response): Promise<JsonPayload> {
  try {
    return (await response.json()) as JsonPayload;
  } catch {
    return null;
  }
}

export async function GET(): Promise<Response> {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  try {
    const response = await fetch(buildBackendUrl(DATASETS_OVERVIEW_ENDPOINT), {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    const payload = await readJsonSafely(response);

    if (!response.ok) {
      return NextResponse.json(
        { detail: payload?.detail ?? "Failed to load datasets overview" },
        { status: response.status },
      );
    }

    return NextResponse.json(payload);
  } catch (error) {
    console.error("Failed to load datasets overview:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
