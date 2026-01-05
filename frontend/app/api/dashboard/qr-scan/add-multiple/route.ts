// frontend/app/api/dashboard/qr-scan/add-multiple/route.ts
// Proxies QR scan add-multiple submissions from the Next.js client to the api_v3 backend.
// Exists to keep auth tokens server-side while supporting bulk barcode capture.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const MULTIPLE_SAMPLES_ENDPOINT = "/api/v3/multiple-samples/";

export async function POST(request: Request) {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    let payload: unknown = null;
    try {
      payload = await request.json();
    } catch {
      return NextResponse.json({ detail: "Invalid payload" }, { status: 400 });
    }

    const response = await fetch(buildBackendUrl(MULTIPLE_SAMPLES_ENDPOINT), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload ?? {}),
    });

    let data: unknown = null;
    try {
      data = await response.json();
    } catch {
      data = null;
    }

    if (!response.ok) {
      return NextResponse.json(data ?? { detail: "Failed to save sample" }, {
        status: response.status,
      });
    }

    return NextResponse.json(data ?? { success: true });
  } catch (error) {
    console.error("Failed to submit multiple sample:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
