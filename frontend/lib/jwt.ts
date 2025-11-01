// frontend/lib/jwt.ts
// Provides utility helpers for decoding and inspecting JWT payloads on the frontend.
// Exists so authentication logic (middleware, API routes, components) can safely reason about token expiry.

import { ACCESS_TOKEN_REFRESH_THRESHOLD } from "@/lib/auth";

type JwtPayload = {
  exp?: number;
  [key: string]: unknown;
};

function decodeBase64UrlSegment(segment: string): string {
  const base64 = segment.replace(/-/g, "+").replace(/_/g, "/");
  const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), "=");

  if (typeof atob === "function") {
    // Edge runtime & browser path.
    return decodeURIComponent(
      Array.from(atob(padded))
        .map((char) => `%${char.charCodeAt(0).toString(16).padStart(2, "0")}`)
        .join(""),
    );
  }

  // Node.js fallback.
  return Buffer.from(padded, "base64").toString("utf-8");
}

export function parseJwt(token: string): JwtPayload | null {
  const segments = token.split(".");

  if (segments.length < 2) {
    return null;
  }

  try {
    const payloadJson = decodeBase64UrlSegment(segments[1]);
    return JSON.parse(payloadJson) as JwtPayload;
  } catch {
    return null;
  }
}

export function isJwtExpired(token: string, skewSeconds = 0): boolean {
  const payload = parseJwt(token);
  if (!payload?.exp || typeof payload.exp !== "number") {
    return true;
  }

  const expiresAt = payload.exp * 1000;
  const nowWithSkew = Date.now() + skewSeconds * 1000;
  return expiresAt <= nowWithSkew;
}

export function shouldRefreshAccessToken(token: string): boolean {
  return isJwtExpired(token, ACCESS_TOKEN_REFRESH_THRESHOLD);
}
