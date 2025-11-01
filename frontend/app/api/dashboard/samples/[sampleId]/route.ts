// frontend/app/api/dashboard/samples/[sampleId]/route.ts
// Exposes a server-side proxy for fetching individual sample records from the Django API.
// Avoids leaking HTTP-only JWTs to the client when loading sample detail pages.

import { cookies } from "next/headers";
import { type NextRequest, NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const SAMPLES_ENDPOINT = "/api/v3/samples/";

export async function GET(
  _request: NextRequest,
  context: RouteContext<"/api/dashboard/samples/[sampleId]">,
) {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;
    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const params = await context.params;
    const sampleId = params.sampleId;
    if (!sampleId) {
      return NextResponse.json({ detail: "Missing sample identifier" }, { status: 400 });
    }

    const encodedId = encodeURIComponent(sampleId);
    const response = await fetch(buildBackendUrl(`${SAMPLES_ENDPOINT}${encodedId}/`), {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json({ detail: "Failed to fetch sample" }, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to fetch sample:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
