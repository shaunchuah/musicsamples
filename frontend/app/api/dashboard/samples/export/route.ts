// frontend/app/api/dashboard/samples/export/route.ts
// Exposes a Next.js API endpoint to download all sample records as a CSV file.
// Provides a modern replacement for the legacy Django CSV export, gathering paginated API data server-side.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const SAMPLES_EXPORT_ENDPOINT = "/api/v3/samples/export/";

export async function GET(request: Request): Promise<Response> {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const requestUrl = new URL(request.url);
    const backendUrl = new URL(buildBackendUrl(SAMPLES_EXPORT_ENDPOINT));
    requestUrl.searchParams.forEach((value, key) => {
      if (key !== "page" && key !== "page_size") {
        backendUrl.searchParams.set(key, value);
      }
    });

    const response = await fetch(backendUrl, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        { detail: `Failed to export samples (status ${response.status})` },
        { status: response.status },
      );
    }

    const csvBuffer = await response.arrayBuffer();
    const headers = new Headers();
    headers.set("Cache-Control", "no-store");
    const contentType = response.headers.get("Content-Type");
    if (contentType) {
      headers.set("Content-Type", contentType);
    }
    const contentDisposition = response.headers.get("Content-Disposition");
    if (contentDisposition) {
      headers.set("Content-Disposition", contentDisposition);
    }

    return new NextResponse(csvBuffer, { headers });
  } catch (error) {
    console.error("Failed to export samples CSV:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
