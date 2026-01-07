// frontend/app/api/auth/logout/route.ts
// Exposes a Next.js API route that revokes the refresh token and clears auth cookies.
// Enables the React client to sign users out without direct backend interaction.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl, REFRESH_COOKIE_NAME } from "@/lib/auth";

export async function POST(): Promise<Response> {
  const response = NextResponse.json({ success: true });

  const cookieStore = await cookies();
  const refreshToken = cookieStore.get(REFRESH_COOKIE_NAME)?.value;

  if (refreshToken) {
    try {
      await fetch(buildBackendUrl("/api/v3/auth/blacklist/"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });
    } catch {
      // Swallow backend failures; logout should still succeed locally.
    }
  }

  response.cookies.set({
    name: AUTH_COOKIE_NAME,
    value: "",
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 0,
  });

  response.cookies.set({
    name: REFRESH_COOKIE_NAME,
    value: "",
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 0,
  });

  return response;
}
