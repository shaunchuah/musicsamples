// frontend/app/api/auth/change-password/route.ts
// Proxies authenticated password change requests from the Next.js app to the Django backend.
// Exists so the SPA can update passwords while keeping auth tokens server-side.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

type ChangePasswordPayload = {
  newPassword?: unknown;
  confirmPassword?: unknown;
};

type BackendPasswordChangeResponse = {
  error?: string;
  success?: boolean;
};

export async function POST(request: Request): Promise<Response> {
  let newPassword: string | undefined;
  let confirmPassword: string | undefined;

  try {
    const body = (await request.json()) as ChangePasswordPayload;
    newPassword = typeof body.newPassword === "string" ? body.newPassword : undefined;
    confirmPassword = typeof body.confirmPassword === "string" ? body.confirmPassword : undefined;
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  if (!newPassword || !confirmPassword) {
    return NextResponse.json(
      { error: "New password and confirmation are required." },
      { status: 400 },
    );
  }

  if (newPassword !== confirmPassword) {
    return NextResponse.json({ error: "Passwords do not match." }, { status: 400 });
  }

  const cookieStore = await cookies();
  const token = cookieStore.get(AUTH_COOKIE_NAME)?.value ?? null;

  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  let backendResponse: Response;

  try {
    backendResponse = await fetch(buildBackendUrl("/api/v3/users/me/password/"), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ new_password: newPassword }),
    });
  } catch {
    return NextResponse.json({ error: "Password change service is unavailable." }, { status: 502 });
  }

  let backendPayload: BackendPasswordChangeResponse | null = null;
  try {
    backendPayload = (await backendResponse.json()) as BackendPasswordChangeResponse;
  } catch {
    // Ignore parse failures; handled below.
  }

  if (!backendResponse.ok) {
    const errorMessage = backendPayload?.error || "Unable to change password.";
    return NextResponse.json({ error: errorMessage }, { status: backendResponse.status || 400 });
  }

  return NextResponse.json({ success: true });
}
