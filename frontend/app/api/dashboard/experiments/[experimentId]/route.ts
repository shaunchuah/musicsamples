// frontend/app/api/dashboard/experiments/[experimentId]/route.ts
// Proxies update requests for a single experiment to the Django api/v3 endpoint.
// Exists to keep auth cookies server-side while enabling experiment edits from the dashboard.

import { cookies } from "next/headers";
import { type NextRequest, NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const EXPERIMENTS_ENDPOINT = "/api/v3/experiments/";

async function proxyExperimentDelete(
  context: RouteContext<"/api/dashboard/experiments/[experimentId]">,
) {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;
    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const params = await context.params;
    const experimentId = params.experimentId;
    if (!experimentId) {
      return NextResponse.json({ detail: "Missing experiment identifier" }, { status: 400 });
    }

    const encodedId = encodeURIComponent(experimentId);
    const response = await fetch(buildBackendUrl(`${EXPERIMENTS_ENDPOINT}${encodedId}/`), {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      return NextResponse.json(data ?? { detail: "Failed to delete experiment" }, {
        status: response.status,
      });
    }

    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    return NextResponse.json(data ?? {});
  } catch (error) {
    console.error("Failed to delete experiment:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}

async function proxyExperimentUpdate(
  request: NextRequest,
  context: RouteContext<"/api/dashboard/experiments/[experimentId]">,
  method: "PATCH" | "PUT",
) {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;
    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const params = await context.params;
    const experimentId = params.experimentId;
    if (!experimentId) {
      return NextResponse.json({ detail: "Missing experiment identifier" }, { status: 400 });
    }

    const payload = await request.json().catch(() => ({}));
    const encodedId = encodeURIComponent(experimentId);
    const response = await fetch(buildBackendUrl(`${EXPERIMENTS_ENDPOINT}${encodedId}/`), {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      return NextResponse.json(data ?? { detail: "Failed to update experiment" }, {
        status: response.status,
      });
    }

    return NextResponse.json(data ?? {});
  } catch (error) {
    console.error("Failed to update experiment:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}

export async function PATCH(
  request: NextRequest,
  context: RouteContext<"/api/dashboard/experiments/[experimentId]">,
) {
  return proxyExperimentUpdate(request, context, "PATCH");
}

export async function PUT(
  request: NextRequest,
  context: RouteContext<"/api/dashboard/experiments/[experimentId]">,
) {
  return proxyExperimentUpdate(request, context, "PUT");
}

export async function DELETE(
  _request: NextRequest,
  context: RouteContext<"/api/dashboard/experiments/[experimentId]">,
) {
  return proxyExperimentDelete(context);
}
