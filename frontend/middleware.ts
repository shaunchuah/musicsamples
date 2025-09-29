// frontend/middleware.ts
// Intercepts requests to enforce authentication across protected routes.
// Guarantees that unauthenticated users are redirected to the login page while preserving their destination.

import { NextResponse, type NextRequest } from "next/server";

import { AUTH_COOKIE_NAME } from "@/lib/auth";

const PUBLIC_FILE = /\.(.*)$/;
const PUBLIC_PATHS = new Set(["/login"]);

export function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const isPublicFile = PUBLIC_FILE.test(pathname);
  const isNextAsset = pathname.startsWith("/_next");
  const isAuthApiRoute = pathname.startsWith("/api/auth");

  if (isPublicFile || isNextAsset || isAuthApiRoute) {
    return NextResponse.next();
  }

  const token = request.cookies.get(AUTH_COOKIE_NAME)?.value;

  if (PUBLIC_PATHS.has(pathname)) {
    if (token) {
      const redirectUrl = request.nextUrl.clone();
      redirectUrl.pathname = "/";
      redirectUrl.search = "";
      return NextResponse.redirect(redirectUrl);
    }
    return NextResponse.next();
  }

  if (!token) {
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

    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|manifest.json|robots.txt|sitemap.xml).*)"],
};
