// middleware.ts
import { withAuth } from "next-auth/middleware"
import { NextResponse } from "next/server"
import { useSession } from "next-auth/react";

export default withAuth(
  function middleware(req) {
    // Return early if it's the root path
    if (req.nextUrl.pathname === "/") {
      return NextResponse.next()
    }

    // Check session exists for all other routes
    return NextResponse.next()
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token
    },
  }
)

export const config = {
  // Match all paths except root, api, and auth endpoints
  matcher: ["/((?!api|auth|_next|$).*)"]
}
