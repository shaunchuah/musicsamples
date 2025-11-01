# Frontend Authentication Security Analysis

## Current Authentication Architecture

The Next.js frontend now exchanges credentials for a JWT access/refresh pair via Django's SimpleJWT endpoints. Access tokens (`authToken`) and refresh tokens (`refreshToken`) are stored in HTTP-only cookies. Middleware inspects the access token on every request, silently rotating it when expiration nears by calling `/api/token/refresh/` and updating both cookies. Logout clears both cookies and invokes Django's blacklist endpoint so the refresh token cannot be reused. Legacy DRF token endpoints remain available for manual API access through the Django UI, but the SPA no longer depends on them.

## Security Strengths

✅ **HTTP-Only Cookies**: Both access and refresh tokens live in HTTP-only cookies, keeping them out of reach of client-side scripts.

✅ **Silent Refresh**: Middleware transparently refreshes expiring access tokens using the rotated refresh token, preventing surprise logouts while keeping access tokens short lived.

✅ **Secure Cookie Configuration**:

- `secure` flag set in production
- `sameSite: "lax"` adds CSRF resistance for top-level navigations
- Access cookie lifetime matches the 60-minute backend expiry; refresh cookie aligns with the 1-day rotation window

✅ **Backend Blacklisting**: Refresh tokens are blacklisted during logout, ensuring immediate revocation across devices that share cookie state.

✅ **Proper CORS + CSRF**: CORS settings remain locked to known origins and Django's CSRF middleware stays enabled for state-changing operations.

## Security Issues and Recommendations

### 🔴 **Critical: No Authenticated API Calls Yet**

Protected data fetches still need to be implemented. When wiring them in, proxy through Next.js API routes or server components to append the `Authorization: Bearer <access>` header server-side:

```typescript
export async function GET() {
  const token = cookies().get('authToken')?.value;
  if (!token) return NextResponse.redirect('/login');

  const response = await fetch(`${getBackendBaseUrl()}/api/data/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: 'no-store',
  });

  return NextResponse.json(await response.json());
}
```

Avoid exposing tokens to client-side JavaScript.

### 🟡 **Rate Limiting Still Missing**

`/api/token/` and `/api/token/refresh/` are unthrottled. Add DRF throttling or Django middleware to slow brute-force attempts against login and refresh endpoints.

### 🟡 **Mixed Authentication Modes**

SimpleJWT, session auth, and DRF token auth are enabled simultaneously. The SPA now relies solely on JWT, but long-lived DRF tokens issued via the Django UI remain valid until manually revoked. Plan to migrate those manual API keys or tighten their scope to reduce exposure.

### 🟢 **Session Invalidation**

Logout blacklists refresh tokens, but remember that blacklisting requires regular cleanup and rotates the token set per use. Monitor the blacklist table size and consider periodic pruning.

## Overall Assessment

The frontend now employs rotating JWT access and refresh tokens with silent renewal, significantly improving session hygiene compared to the previous single-use DRF token cookie. Remaining work focuses on protecting the authentication endpoints with throttling, migrating any manual DRF token use cases, and ensuring future API integrations keep token handling server-side.

**Next Actions:**

1. Route upcoming API calls through Next.js server contexts and attach `Bearer` headers automatically.
2. Enable throttling/rate limiting on login and refresh endpoints.
3. Design a replacement for legacy DRF tokens (or aggressively monitor and expire them) before deprecating token authentication entirely.
