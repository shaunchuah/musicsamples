// frontend/lib/auth.ts
// Centralises shared authentication helpers for the Next.js frontend.
// Enables consistent handling of backend URLs and auth cookie names across middleware, API routes, and components.

const DEFAULT_BACKEND_URL =
	process.env.NODE_ENV === "production"
		? "https://samples.musicstudy.uk"
		: "http://localhost:8000";

export const AUTH_COOKIE_NAME = "authToken";
export const REFRESH_COOKIE_NAME = "refreshToken";

export const ACCESS_TOKEN_MAX_AGE = 60 * 60; // 1 hour
export const REFRESH_COOKIE_MAX_AGE = 60 * 60 * 24; // 1 day
export const ACCESS_TOKEN_REFRESH_THRESHOLD = 60; // Seconds before expiry to refresh silently

export function getBackendBaseUrl(): string {
	const url =
		process.env.BACKEND_URL ||
		process.env.NEXT_PUBLIC_BACKEND_URL ||
		DEFAULT_BACKEND_URL;
	return url.endsWith("/") ? url.slice(0, -1) : url;
}

export function buildBackendUrl(path: string): string {
	const normalisedPath = path.startsWith("/") ? path : `/${path}`;
	return `${getBackendBaseUrl()}${normalisedPath}`;
}
