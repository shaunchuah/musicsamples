// frontend/app/api/auth/login/route.ts
// Proxies credential-based authentication requests to the Django backend.
// Provides a Next.js API endpoint that stores rotated access/refresh JWTs inside HTTP-only cookies for the SPA.

import { NextResponse } from "next/server";

import {
  ACCESS_TOKEN_MAX_AGE,
  AUTH_COOKIE_NAME,
  buildBackendUrl,
  REFRESH_COOKIE_MAX_AGE,
  REFRESH_COOKIE_NAME,
} from "@/lib/auth";

const AUTH_DEBUG_ENABLED = process.env.AUTH_DEBUG === "true";

type LoginPayload = {
  email?: unknown;
  password?: unknown;
};

type BackendTokenResponse = {
  access?: string;
  refresh?: string;
  detail?: string;
  non_field_errors?: string[];
};

export async function POST(request: Request): Promise<Response> {
  let email: string | undefined;
  let password: string | undefined;

  try {
    const body = (await request.json()) as LoginPayload;
    email = typeof body.email === "string" ? body.email.trim() : undefined;
    password = typeof body.password === "string" ? body.password : undefined;
  } catch (error) {
    console.error("[login] Failed to parse request body", { error });
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  if (!email || !password) {
    console.error("[login] Missing credentials", { hasEmail: Boolean(email), hasPassword: Boolean(password) });
    return NextResponse.json({ error: "Email and password are required." }, { status: 400 });
  }

  let backendResponse: Response;
  const backendUrl = buildBackendUrl("/api/token/");

  try {
    console.info("[login] Proxying auth request", { email, backendUrl });
    backendResponse = await fetch(backendUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });
  } catch (error) {
    console.error("[login] Backend fetch failed", { backendUrl, error });
    const payload: Record<string, unknown> = { error: "Authentication service is unavailable." };
    if (AUTH_DEBUG_ENABLED) {
      payload.debug = { backendUrl, reason: "fetch_failed" };
    }
    return NextResponse.json(payload, { status: 502 });
  }

  let backendJson: BackendTokenResponse | null = null;
  try {
    backendJson = (await backendResponse.json()) as BackendTokenResponse;
  } catch {
    // ignore parse failures; handled below
  }

  if (!backendResponse.ok) {
    console.error("[login] Backend rejected credentials", {
      email,
      backendStatus: backendResponse.status,
      backendBody: backendJson,
    });
    const errorMessage =
      backendJson?.detail || backendJson?.non_field_errors?.[0] || "Invalid email or password.";
    const payload: Record<string, unknown> = { error: errorMessage };
    if (AUTH_DEBUG_ENABLED) {
      payload.debug = {
        backendUrl,
        backendStatus: backendResponse.status,
        backendBody: backendJson,
      };
    }

    return NextResponse.json(payload, { status: backendResponse.status || 401 });
  }

  const accessToken = backendJson?.access;
  const refreshToken = backendJson?.refresh;

  if (!accessToken || !refreshToken) {
    console.error("[login] Backend response missing tokens", { email, backendBody: backendJson });
    const payload: Record<string, unknown> = {
      error: "Authentication tokens missing from backend response.",
    };
    if (AUTH_DEBUG_ENABLED) {
      payload.debug = {
        backendUrl,
        backendBody: backendJson,
        reason: "missing_tokens",
      };
    }
    return NextResponse.json(payload, { status: 502 });
  }

  console.info("[login] Authentication succeeded", { email });
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
    value: refreshToken,
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: REFRESH_COOKIE_MAX_AGE,
  });

  return response;
}
