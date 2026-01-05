// frontend/app/api/dashboard/samples/filters/route.ts
// Proxies sample filter metadata requests to the Django api/v3 filters endpoint.
// Exists to keep auth cookies server-side while powering dashboard filter dropdowns.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const SAMPLE_FILTERS_ENDPOINT = "/api/v3/samples/filters/";

export async function GET() {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const response = await fetch(buildBackendUrl(SAMPLE_FILTERS_ENDPOINT), {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        { detail: "Failed to fetch sample filter options" },
        { status: response.status },
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to fetch sample filter options:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
