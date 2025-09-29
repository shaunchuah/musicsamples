// frontend/app/api/auth/logout/route.ts
// Exposes a Next.js API route that clears the authentication cookie.
// Enables the React client to sign users out without direct backend interaction.

import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME } from "@/lib/auth";

export async function POST(): Promise<Response> {
  const response = NextResponse.json({ success: true });

  response.cookies.set({
    name: AUTH_COOKIE_NAME,
    value: "",
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 0,
  });

  return response;
}
