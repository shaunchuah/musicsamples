// frontend/app/api/auth/reset-password/route.ts
// Proxies password reset confirmation requests from the Next.js app to the Django backend.
// Lets the SPA submit UID/token/password data securely without exposing backend URLs in the client.

import { NextResponse } from "next/server";

import { buildBackendUrl } from "@/lib/auth";

type ResetPasswordPayload = {
  uid?: unknown;
  token?: unknown;
  newPassword?: unknown;
};

type BackendResetResponse = {
  error?: string;
  success?: boolean;
};

export async function POST(request: Request): Promise<Response> {
  let uid: string | undefined;
  let token: string | undefined;
  let newPassword: string | undefined;

  try {
    const body = (await request.json()) as ResetPasswordPayload;
    uid = typeof body.uid === "string" ? body.uid : undefined;
    token = typeof body.token === "string" ? body.token : undefined;
    newPassword = typeof body.newPassword === "string" ? body.newPassword : undefined;
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  if (!uid || !token || !newPassword) {
    return NextResponse.json({ error: "All fields are required." }, { status: 400 });
  }

  let backendResponse: Response;

  try {
    backendResponse = await fetch(buildBackendUrl("/api/password-reset/confirm/"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        uid,
        token,
        new_password: newPassword,
      }),
    });
  } catch {
    return NextResponse.json({ error: "Password reset service is unavailable." }, { status: 502 });
  }

  let backendPayload: BackendResetResponse | null = null;
  try {
    backendPayload = (await backendResponse.json()) as BackendResetResponse;
  } catch {
    // ignore parse failures; handled below
  }

  if (!backendResponse.ok) {
    const errorMessage = backendPayload?.error || "Unable to reset password.";
    return NextResponse.json({ error: errorMessage }, { status: backendResponse.status || 400 });
  }

  return NextResponse.json({ success: true });
}
