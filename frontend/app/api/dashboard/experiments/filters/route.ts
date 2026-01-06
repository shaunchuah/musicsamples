// frontend/app/api/dashboard/experiments/filters/route.ts
// Proxies experiment filter option requests to the Django api/v3 endpoint.
// Exists to centralize experiment filter option loading within the Next.js dashboard.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const EXPERIMENT_FILTERS_ENDPOINT = "/api/v3/experiments/filters/";

export async function GET() {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;
    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const response = await fetch(buildBackendUrl(EXPERIMENT_FILTERS_ENDPOINT), {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      const errorPayload = await response.json().catch(() => null);
      return NextResponse.json(errorPayload ?? { detail: "Failed to fetch experiment filters" }, {
        status: response.status,
      });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to fetch experiment filters:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
