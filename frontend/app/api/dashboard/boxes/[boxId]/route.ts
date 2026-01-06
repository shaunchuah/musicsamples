// frontend/app/api/dashboard/boxes/[boxId]/route.ts
// Proxies update requests for a single box to the Django api/v3 endpoint.
// Exists to keep auth cookies server-side while enabling box edits from the dashboard.

import { cookies } from "next/headers";
import { type NextRequest, NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const BOXES_ENDPOINT = "/api/v3/boxes/";

async function proxyBoxDelete(context: RouteContext<"/api/dashboard/boxes/[boxId]">) {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;
    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const params = await context.params;
    const boxId = params.boxId;
    if (!boxId) {
      return NextResponse.json({ detail: "Missing box identifier" }, { status: 400 });
    }

    const encodedId = encodeURIComponent(boxId);
    const response = await fetch(buildBackendUrl(`${BOXES_ENDPOINT}${encodedId}/`), {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      return NextResponse.json(data ?? { detail: "Failed to mark box as used" }, {
        status: response.status,
      });
    }

    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    return NextResponse.json(data ?? {});
  } catch (error) {
    console.error("Failed to mark box as used:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}

async function proxyBoxUpdate(
  request: NextRequest,
  context: RouteContext<"/api/dashboard/boxes/[boxId]">,
  method: "PATCH" | "PUT",
) {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;
    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const params = await context.params;
    const boxId = params.boxId;
    if (!boxId) {
      return NextResponse.json({ detail: "Missing box identifier" }, { status: 400 });
    }

    const payload = await request.json().catch(() => ({}));
    const encodedId = encodeURIComponent(boxId);
    const response = await fetch(buildBackendUrl(`${BOXES_ENDPOINT}${encodedId}/`), {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      return NextResponse.json(data ?? { detail: "Failed to update box" }, {
        status: response.status,
      });
    }

    return NextResponse.json(data ?? {});
  } catch (error) {
    console.error("Failed to update box:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}

export async function PATCH(
  request: NextRequest,
  context: RouteContext<"/api/dashboard/boxes/[boxId]">,
) {
  return proxyBoxUpdate(request, context, "PATCH");
}

export async function PUT(
  request: NextRequest,
  context: RouteContext<"/api/dashboard/boxes/[boxId]">,
) {
  return proxyBoxUpdate(request, context, "PUT");
}

export async function DELETE(
  _request: NextRequest,
  context: RouteContext<"/api/dashboard/boxes/[boxId]">,
) {
  return proxyBoxDelete(context);
}
