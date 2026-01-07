// frontend/app/api/dashboard/study-ids/[studyId]/route.ts
// Proxies delete requests for a single study ID to the Django api/v3 endpoint.
// Exists to keep auth cookies server-side while enabling staff-only deletes from the dashboard.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const STUDY_IDS_ENDPOINT = "/api/v3/study-ids/";

export async function DELETE(
  _request: Request,
  context: RouteContext<"/api/dashboard/study-ids/[studyId]">,
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
    const response = await fetch(buildBackendUrl(`${STUDY_IDS_ENDPOINT}${encodedId}/`), {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      return NextResponse.json(payload ?? { detail: "Failed to delete study ID" }, {
        status: response.status,
      });
    }

    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    return NextResponse.json(payload ?? {});
  } catch (error) {
    console.error("Failed to delete study ID:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
