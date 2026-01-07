// frontend/app/api/dashboard/datasets/[datasetName]/export/route.ts
// Proxies dataset CSV downloads to the Django api_v3 export endpoint with server-side auth.
// Exists so the Next.js frontend can export datasets without exposing JWTs to the browser.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const DATASET_EXPORT_PREFIX = "/api/v3/datasets/";

export async function GET(
  _request: Request,
  context: RouteContext<"/api/dashboard/datasets/[datasetName]/export">,
): Promise<Response> {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  const params = await context.params;
  const datasetName = params.datasetName;

  if (!datasetName) {
    return NextResponse.json({ detail: "Missing dataset name" }, { status: 400 });
  }

  const encodedName = encodeURIComponent(datasetName);

  try {
    const response = await fetch(
      buildBackendUrl(`${DATASET_EXPORT_PREFIX}${encodedName}/export-csv/`),
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        cache: "no-store",
      },
    );

    if (!response.ok) {
      return NextResponse.json(
        { detail: `Failed to export dataset (status ${response.status})` },
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
    console.error("Failed to export dataset CSV:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
