// frontend/middleware.ts
// Intercepts requests to enforce authentication across protected routes.
// Guarantees that unauthenticated users are redirected to the login page while preserving their destination.

import { type NextRequest, NextResponse } from "next/server";

import {
  ACCESS_TOKEN_MAX_AGE,
  AUTH_COOKIE_NAME,
  buildBackendUrl,
  REFRESH_COOKIE_MAX_AGE,
  REFRESH_COOKIE_NAME,
} from "@/lib/auth";
import { isJwtExpired, shouldRefreshAccessToken } from "@/lib/jwt";

const PUBLIC_FILE = /\.(.*)$/;
const PUBLIC_PATHS = new Set(["/login", "/forgot-password"]);

type RefreshedTokens = {
  access: string;
  refresh: string;
};

async function refreshTokens(refreshToken: string): Promise<RefreshedTokens | null> {
  try {
    const backendResponse = await fetch(buildBackendUrl("/api/token/refresh/"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!backendResponse.ok) {
      return null;
    }

    const data = (await backendResponse.json()) as RefreshedTokens;

    if (!data?.access || !data?.refresh) {
      return null;
    }

    return data;
  } catch {
    return null;
  }
}

export async function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const isPublicFile = PUBLIC_FILE.test(pathname);
  const isNextAsset = pathname.startsWith("/_next");
  const isAuthApiRoute = pathname.startsWith("/api/auth");

  if (isPublicFile || isNextAsset || isAuthApiRoute) {
    return NextResponse.next();
  }

  let accessToken = request.cookies.get(AUTH_COOKIE_NAME)?.value ?? null;
  const refreshTokenCookie = request.cookies.get(REFRESH_COOKIE_NAME)?.value ?? null;

  type CookieOperation = {
    name: string;
    value: string;
    maxAge: number;
  };

  const cookieOperations: CookieOperation[] = [];

  let shouldAttemptRefresh = false;
  let refreshTokenForUse: string | null = null;

  if (typeof refreshTokenCookie === "string") {
    if (!accessToken) {
      shouldAttemptRefresh = true;
      refreshTokenForUse = refreshTokenCookie;
    } else if (shouldRefreshAccessToken(accessToken)) {
      shouldAttemptRefresh = true;
      refreshTokenForUse = refreshTokenCookie;
    }
  }

  if (shouldAttemptRefresh && refreshTokenForUse) {
    const refreshed = await refreshTokens(refreshTokenForUse);

    if (refreshed) {
      accessToken = refreshed.access;
      cookieOperations.push(
        {
          name: AUTH_COOKIE_NAME,
          value: refreshed.access,
          maxAge: ACCESS_TOKEN_MAX_AGE,
        },
        {
          name: REFRESH_COOKIE_NAME,
          value: refreshed.refresh,
          maxAge: REFRESH_COOKIE_MAX_AGE,
        },
      );
    } else {
      cookieOperations.push(
        {
          name: AUTH_COOKIE_NAME,
          value: "",
          maxAge: 0,
        },
        {
          name: REFRESH_COOKIE_NAME,
          value: "",
          maxAge: 0,
        },
      );
      accessToken = null;
    }
  }

  const applyCookies = (res: NextResponse) => {
    for (const op of cookieOperations) {
      res.cookies.set({
        name: op.name,
        value: op.value,
        httpOnly: true,
        sameSite: "lax",
        secure: process.env.NODE_ENV === "production",
        path: "/",
        maxAge: op.maxAge,
      });
    }
    return res;
  };

  if (PUBLIC_PATHS.has(pathname)) {
    if (accessToken && !isJwtExpired(accessToken)) {
      const redirectUrl = request.nextUrl.clone();
      redirectUrl.pathname = "/";
      redirectUrl.search = "";
      return applyCookies(NextResponse.redirect(redirectUrl));
    }
    return applyCookies(NextResponse.next());
  }

  if (!accessToken || isJwtExpired(accessToken)) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = "/login";
    loginUrl.search = "";

    const searchSuffix = search ?? "";
    const normalisedSearch = searchSuffix.startsWith("?") ? searchSuffix.slice(1) : searchSuffix;
    const redirectTarget =
      pathname === "/"
        ? normalisedSearch
          ? `/?${normalisedSearch}`
          : "/"
        : `${pathname}${searchSuffix}`;

    if (redirectTarget && redirectTarget !== "/") {
      loginUrl.searchParams.set("next", redirectTarget);
    }

    return applyCookies(NextResponse.redirect(loginUrl));
  }

  return applyCookies(NextResponse.next());
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|manifest.json|robots.txt|sitemap.xml).*)"],
};
