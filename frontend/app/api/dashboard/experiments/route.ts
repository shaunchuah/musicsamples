// frontend/app/api/dashboard/experiments/route.ts
// Proxies create requests for experiments to the Django api/v3 endpoint.
// Exists to keep auth cookies server-side while enabling experiment creation from the dashboard.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const EXPERIMENTS_ENDPOINT = "/api/v3/experiments/";

export async function POST(request: Request) {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const payload = await request.json();

    const response = await fetch(buildBackendUrl(EXPERIMENTS_ENDPOINT), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorPayload = await response.json().catch(() => null);
      return NextResponse.json(errorPayload ?? { detail: "Failed to create experiment" }, {
        status: response.status,
      });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to create experiment:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
