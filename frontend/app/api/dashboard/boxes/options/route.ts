// frontend/app/api/dashboard/boxes/options/route.ts
// Proxies basic science box form metadata requests to the Django api/v3 endpoint.
// Exists to keep auth cookies server-side while powering the box creation dialog.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const BOX_OPTIONS_ENDPOINT = "/api/v3/boxes/options/";

export async function GET() {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const response = await fetch(buildBackendUrl(BOX_OPTIONS_ENDPOINT), {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        { detail: "Failed to fetch box options" },
        { status: response.status },
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to fetch box options:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
