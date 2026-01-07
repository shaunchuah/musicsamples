// frontend/app/api/auth/refresh/route.ts
// Refreshes rotated JWT credentials by proxying token refresh requests to the Django backend.
// Exists to keep the SPA session alive without exposing backend endpoints directly to the browser.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import {
  ACCESS_TOKEN_MAX_AGE,
  AUTH_COOKIE_NAME,
  buildBackendUrl,
  REFRESH_COOKIE_MAX_AGE,
  REFRESH_COOKIE_NAME,
} from "@/lib/auth";

type BackendTokenResponse = {
  access?: string;
  refresh?: string;
  detail?: string;
};

export async function POST(): Promise<Response> {
  const cookieStore = await cookies();
  const refreshToken = cookieStore.get(REFRESH_COOKIE_NAME)?.value;

  if (!refreshToken) {
    return NextResponse.json({ error: "Refresh token missing." }, { status: 401 });
  }

  let backendResponse: Response;

  try {
    backendResponse = await fetch(buildBackendUrl("/api/v3/auth/refresh/"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });
  } catch {
    return NextResponse.json({ error: "Token refresh service unavailable." }, { status: 502 });
  }

  let backendJson: BackendTokenResponse | null = null;
  try {
    backendJson = (await backendResponse.json()) as BackendTokenResponse;
  } catch {
    // Ignore parsing errors; addressed below.
  }

  if (!backendResponse.ok) {
    const errorMessage = backendJson?.detail || "Unable to refresh session.";
    return NextResponse.json({ error: errorMessage }, { status: backendResponse.status || 401 });
  }

  const accessToken = backendJson?.access;
  const rotatedRefreshToken = backendJson?.refresh;

  if (!accessToken || !rotatedRefreshToken) {
    return NextResponse.json({ error: "Refresh response missing tokens." }, { status: 502 });
  }

  const response = NextResponse.json({ success: true });

  response.cookies.set({
    name: AUTH_COOKIE_NAME,
    value: accessToken,
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: ACCESS_TOKEN_MAX_AGE,
  });

  response.cookies.set({
    name: REFRESH_COOKIE_NAME,
    value: rotatedRefreshToken,
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: REFRESH_COOKIE_MAX_AGE,
  });

  return response;
}
