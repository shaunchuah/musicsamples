// frontend/app/api/dashboard/qr-scan/mark-used/route.ts
// Proxies QR scan mark-used requests from the Next.js client to the api_v3 backend.
// Exists to keep auth tokens server-side while marking samples as used.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const SAMPLE_USED_ENDPOINT = "/api/v3/samples-used/";

type MarkUsedPayload = {
  sample_id?: unknown;
};

export async function PUT(request: Request) {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    let payload: MarkUsedPayload = {};
    try {
      payload = (await request.json()) as MarkUsedPayload;
    } catch {
      return NextResponse.json({ detail: "Invalid payload" }, { status: 400 });
    }

    const sampleId = typeof payload.sample_id === "string" ? payload.sample_id.trim() : "";
    if (!sampleId) {
      return NextResponse.json({ detail: "Sample ID is required" }, { status: 400 });
    }

    const response = await fetch(
      buildBackendUrl(`${SAMPLE_USED_ENDPOINT}${encodeURIComponent(sampleId)}/`),
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sample_id: sampleId,
          is_used: true,
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
      return NextResponse.json(data ?? { detail: "Failed to mark sample as used" }, {
        status: response.status,
      });
    }

    return NextResponse.json(data ?? { success: true });
  } catch (error) {
    console.error("Failed to mark sample as used:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
