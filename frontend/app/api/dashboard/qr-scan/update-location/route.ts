// frontend/app/api/dashboard/qr-scan/update-location/route.ts
// Proxies QR scan location updates from the Next.js client to the api_v3 backend.
// Exists to keep auth tokens server-side while updating sample locations by barcode.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const SAMPLE_LOCATION_ENDPOINT = "/api/v3/sample-location/";

type UpdateLocationPayload = {
  sample_id?: unknown;
  sample_location?: unknown;
  sample_sublocation?: unknown;
};

export async function PUT(request: Request) {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    let payload: UpdateLocationPayload = {};
    try {
      payload = (await request.json()) as UpdateLocationPayload;
    } catch {
      return NextResponse.json({ detail: "Invalid payload" }, { status: 400 });
    }

    const sampleId = typeof payload.sample_id === "string" ? payload.sample_id.trim() : "";
    if (!sampleId) {
      return NextResponse.json({ detail: "Sample ID is required" }, { status: 400 });
    }

    const response = await fetch(
      buildBackendUrl(`${SAMPLE_LOCATION_ENDPOINT}${encodeURIComponent(sampleId)}/`),
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sample_id: sampleId,
          sample_location: payload.sample_location ?? "",
          sample_sublocation: payload.sample_sublocation ?? "",
        }),
      },
    );

    let data: unknown = null;
    try {
      data = await response.json();
    } catch {
      data = null;
    }

    if (!response.ok) {
      return NextResponse.json(data ?? { detail: "Failed to update sample" }, {
        status: response.status,
      });
    }

    return NextResponse.json(data ?? { success: true });
  } catch (error) {
    console.error("Failed to update sample location:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
