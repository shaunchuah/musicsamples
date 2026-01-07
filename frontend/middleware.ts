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
const PUBLIC_EXACT_PATHS = new Set(["/login", "/forgot-password", "/unauthorized"]);
const REDIRECT_IF_AUTHENTICATED_PATHS = new Set(["/login", "/forgot-password"]);
const PUBLIC_PATH_PREFIXES = ["/reset-password"];
const UNAUTHORIZED_PATH = "/unauthorized";

type PermissionRule = {
  prefixes: string[];
  requiredGroups?: string[];
  requiresStaff?: boolean;
};

const PERMISSION_RULES: PermissionRule[] = [
  { prefixes: ["/boxes", "/experiments"], requiredGroups: ["basic_science"] },
  { prefixes: ["/datasets"], requiredGroups: ["datasets"] },
  // { prefixes: ["/datastores"], requiredGroups: ["datastores"] },
  { prefixes: ["/users"], requiresStaff: true },
];

type RefreshedTokens = {
  access: string;
  refresh: string;
};

type UserProfile = {
  is_staff?: boolean;
  is_superuser?: boolean;
  groups?: unknown;
};

type UserProfileResult = {
  user: UserProfile | null;
  status: number;
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

function findPermissionRule(pathname: string): PermissionRule | null {
  return (
    PERMISSION_RULES.find((rule) =>
      rule.prefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)),
    ) ?? null
  );
}

function normaliseGroups(groups: unknown): string[] {
  if (Array.isArray(groups)) {
    return groups.filter((value): value is string => typeof value === "string");
  }
  return [];
}

function hasRequiredAccess(profile: UserProfile, rule: PermissionRule): boolean {
  if (profile.is_superuser || profile.is_staff) {
    return true;
  }

  if (rule.requiresStaff) {
    return false;
  }

  const requiredGroups = rule.requiredGroups ?? [];
  if (!requiredGroups.length) {
    return true;
  }

  const groupNames = normaliseGroups(profile.groups).map((group) => group.toLowerCase());
  return requiredGroups.some((group) => groupNames.includes(group.toLowerCase()));
}

async function fetchUserProfile(accessToken: string): Promise<UserProfileResult> {
  try {
    const response = await fetch(buildBackendUrl("/api/v3/users/me/"), {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      return { user: null, status: response.status };
    }

    const data = (await response.json()) as UserProfile;
    return { user: data, status: response.status };
  } catch {
    return { user: null, status: 500 };
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

  const isPublicPath =
    PUBLIC_EXACT_PATHS.has(pathname) ||
    PUBLIC_PATH_PREFIXES.some((prefix) => pathname.startsWith(prefix));

  if (isPublicPath) {
    const shouldRedirectWhenAuthenticated = REDIRECT_IF_AUTHENTICATED_PATHS.has(pathname);

    if (shouldRedirectWhenAuthenticated && accessToken && !isJwtExpired(accessToken)) {
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

  const permissionRule = findPermissionRule(pathname);
  if (permissionRule) {
    const profileResult = await fetchUserProfile(accessToken);
    if (profileResult.status === 401) {
      const loginUrl = request.nextUrl.clone();
      loginUrl.pathname = "/login";
      loginUrl.search = "";
      return applyCookies(NextResponse.redirect(loginUrl));
    }

    if (!profileResult.user || !hasRequiredAccess(profileResult.user, permissionRule)) {
      const unauthorizedUrl = request.nextUrl.clone();
      unauthorizedUrl.pathname = UNAUTHORIZED_PATH;
      unauthorizedUrl.search = "";
      return applyCookies(NextResponse.redirect(unauthorizedUrl));
    }
  }

  return applyCookies(NextResponse.next());
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|manifest.json|robots.txt|sitemap.xml).*)"],
};
