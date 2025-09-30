// frontend/app/login/page.tsx
// Server component that renders the login experience and redirects authenticated users away from the page.
// Ensures the login route stays public while delegating session checks to middleware and cookie inspection.

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { LoginForm } from "@/components/auth/login-form";
import { AUTH_COOKIE_NAME } from "@/lib/auth";
import { isJwtExpired } from "@/lib/jwt";

type LoginPageProps = {
  searchParams?: {
    next?: string;
  };
};

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value;

  if (token && !isJwtExpired(token)) {
    redirect(searchParams?.next && searchParams.next !== "/login" ? searchParams.next : "/");
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-muted/40 px-6 py-12">
      <div className="w-full max-w-sm rounded-xl border border-border bg-background p-8 shadow-lg">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-semibold tracking-tight">Welcome back</h1>
          <p className="text-sm text-muted-foreground">
            Sign in to continue to the Music Samples dashboard.
          </p>
        </div>
        <LoginForm redirectTo={searchParams?.next ?? null} />
      </div>
    </main>
  );
}
