// frontend/app/api/dashboard/samples/search/route.ts
// Proxies the dashboard samples search request to the Django api/v3 search endpoint.
// Exists to keep auth cookies server-side while supporting sample search in the UI.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const SAMPLES_SEARCH_ENDPOINT = "/api/v3/samples/search/";

export async function GET(request: Request) {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const requestUrl = new URL(request.url);
    const backendUrl = new URL(buildBackendUrl(SAMPLES_SEARCH_ENDPOINT));
    requestUrl.searchParams.forEach((value, key) => {
      backendUrl.searchParams.set(key, value);
    });

    if (!backendUrl.searchParams.has("page_size")) {
      backendUrl.searchParams.set("page_size", "100");
    }

    const response = await fetch(backendUrl, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json({ detail: "Failed to fetch samples" }, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to search samples:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
