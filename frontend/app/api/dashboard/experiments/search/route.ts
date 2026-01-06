// frontend/app/api/dashboard/experiments/search/route.ts
// Proxies the dashboard experiments search request to the Django api/v3 search endpoint.
// Exists to keep auth cookies server-side while supporting experiment search in the UI.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

const EXPERIMENTS_SEARCH_ENDPOINT = "/api/v3/experiments/search/";

export async function GET(request: Request) {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const requestUrl = new URL(request.url);
    const backendUrl = new URL(buildBackendUrl(EXPERIMENTS_SEARCH_ENDPOINT));
    requestUrl.searchParams.forEach((value, key) => {
      backendUrl.searchParams.set(key, value);
    });

    if (!backendUrl.searchParams.has("page_size")) {
      backendUrl.searchParams.set("page_size", "20");
    }

    const response = await fetch(backendUrl, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        { detail: "Failed to fetch experiments" },
        { status: response.status },
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to search experiments:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
