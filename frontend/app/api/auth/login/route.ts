// frontend/app/api/auth/login/route.ts
// Proxies credential-based authentication requests to the Django backend.
// Provides a Next.js API endpoint that stores the backend token inside an HTTP-only cookie for the SPA.

import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

type LoginPayload = {
  email?: unknown;
  password?: unknown;
};

type BackendTokenResponse = {
  token?: string;
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
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  if (!email || !password) {
    return NextResponse.json({ error: "Email and password are required." }, { status: 400 });
  }

  let backendResponse: Response;

  try {
    backendResponse = await fetch(buildBackendUrl("/get_api_token/"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username: email, password }),
    });
  } catch {
    return NextResponse.json({ error: "Authentication service is unavailable." }, { status: 502 });
  }

  let backendJson: BackendTokenResponse | null = null;
  try {
    backendJson = (await backendResponse.json()) as BackendTokenResponse;
  } catch {
    // ignore parse failures; handled below
  }

  if (!backendResponse.ok) {
    const errorMessage =
      backendJson?.detail ||
      backendJson?.non_field_errors?.[0] ||
      "Invalid email or password.";

    return NextResponse.json({ error: errorMessage }, { status: backendResponse.status || 401 });
  }

  const token = backendJson?.token;

  if (!token) {
    return NextResponse.json({ error: "Authentication token missing from backend response." }, { status: 502 });
  }

  const response = NextResponse.json({ success: true });

  response.cookies.set({
    name: AUTH_COOKIE_NAME,
    value: token,
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 8,
  });

  return response;
}
