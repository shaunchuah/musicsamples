// frontend/app/api/dashboard/study-ids/[studyId]/files/route.ts
// Proxies study ID file lookups to the Django api/v3 endpoint.
// Exists to keep auth cookies server-side while lazy-loading file dropdowns.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const STUDY_IDS_ENDPOINT = "/api/v3/study-ids/";

export async function GET(
  _request: Request,
  context: RouteContext<"/api/dashboard/study-ids/[studyId]/files">,
) {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;
    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const params = await context.params;
    const studyId = params.studyId;
    if (!studyId) {
      return NextResponse.json({ detail: "Missing study ID" }, { status: 400 });
    }

    const encodedId = encodeURIComponent(studyId);
    const response = await fetch(buildBackendUrl(`${STUDY_IDS_ENDPOINT}${encodedId}/files/`), {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      return NextResponse.json(payload ?? { detail: "Failed to fetch files" }, {
        status: response.status,
      });
    }

    return NextResponse.json(payload ?? []);
  } catch (error) {
    console.error("Failed to load study ID files:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
