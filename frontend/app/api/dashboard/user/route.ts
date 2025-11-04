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
