// frontend/app/api/dashboard/user/route.ts
// Serves the Next.js dashboard with the authenticated user's profile data via the Django backend.
// Exists to keep auth tokens server-side while exposing current user metadata to client components.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const USER_PROFILE_ENDPOINT = "/api/v3/users/me/";

export async function GET(): Promise<Response> {
  const cookieStore = await cookies();
  const token = cookieStore.get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  try {
    const response = await fetch(buildBackendUrl(USER_PROFILE_ENDPOINT), {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      if (response.status === 401) {
        return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
      }

      return NextResponse.json(
        { detail: "Failed to fetch user profile" },
        { status: response.status },
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to fetch user profile:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}

type UserProfileUpdatePayload = {
  first_name?: unknown;
  last_name?: unknown;
  job_title?: unknown;
  primary_organisation?: unknown;
};

export async function PATCH(request: Request): Promise<Response> {
  const cookieStore = await cookies();
  const token = cookieStore.get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  let payload: UserProfileUpdatePayload;
  try {
    payload = (await request.json()) as UserProfileUpdatePayload;
  } catch {
    return NextResponse.json({ detail: "Invalid request body" }, { status: 400 });
  }

  const updatePayload = {
    first_name: typeof payload.first_name === "string" ? payload.first_name.trim() : undefined,
    last_name: typeof payload.last_name === "string" ? payload.last_name.trim() : undefined,
    job_title: typeof payload.job_title === "string" ? payload.job_title.trim() : undefined,
    primary_organisation:
      typeof payload.primary_organisation === "string"
        ? payload.primary_organisation.trim()
        : undefined,
  };

  if (
    !updatePayload.first_name &&
    !updatePayload.last_name &&
    updatePayload.job_title === undefined &&
    updatePayload.primary_organisation === undefined
  ) {
    return NextResponse.json({ detail: "No updates provided" }, { status: 400 });
  }

  try {
    const response = await fetch(buildBackendUrl(USER_PROFILE_ENDPOINT), {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updatePayload),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to update user profile:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
