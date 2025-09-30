// frontend/app/api/auth/forgot-password/route.ts
// Provides a Next.js API endpoint that triggers the Django password reset flow.
// Enables the React forgot-password page to request reset emails without exposing backend internals.

import { NextResponse } from "next/server";

import { buildBackendUrl } from "@/lib/auth";

type ForgotPasswordPayload = {
  email?: unknown;
};

type BackendPasswordResetResponse = {
  error?: string;
  success?: boolean;
};

export async function POST(request: Request): Promise<Response> {
  let email: string | undefined;

  try {
    const body = (await request.json()) as ForgotPasswordPayload;
    email = typeof body.email === "string" ? body.email.trim() : undefined;
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  if (!email) {
    return NextResponse.json({ error: "Email is required." }, { status: 400 });
  }

  let backendResponse: Response;

  try {
    backendResponse = await fetch(buildBackendUrl("/api/password-reset/"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });
  } catch {
    return NextResponse.json({ error: "Password reset service is unavailable." }, { status: 502 });
  }

  let backendPayload: BackendPasswordResetResponse | null = null;
  try {
    backendPayload = (await backendResponse.json()) as BackendPasswordResetResponse;
  } catch {
    // ignore parse failures; handled below
  }

  if (!backendResponse.ok) {
    const errorMessage = backendPayload?.error || "Unable to initiate password reset.";
    return NextResponse.json({ error: errorMessage }, { status: backendResponse.status || 400 });
  }

  return NextResponse.json({ success: true });
}
