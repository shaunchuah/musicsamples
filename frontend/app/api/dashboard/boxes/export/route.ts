// frontend/app/api/dashboard/boxes/export/route.ts
// Exposes a Next.js API endpoint to download boxes as a CSV file.
// Keeps auth tokens server-side while proxying the Django export endpoint.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const BOXES_EXPORT_ENDPOINT = "/api/v3/boxes/export/";

export async function GET(request: Request): Promise<Response> {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const requestUrl = new URL(request.url);
    const backendUrl = new URL(buildBackendUrl(BOXES_EXPORT_ENDPOINT));
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
        { detail: `Failed to export boxes (status ${response.status})` },
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
    console.error("Failed to export boxes CSV:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
