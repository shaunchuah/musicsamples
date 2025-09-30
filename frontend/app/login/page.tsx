// frontend/app/login/page.tsx
// Server component that renders the login experience and redirects authenticated users away from the page.
// Ensures the login route stays public while delegating session checks to middleware and cookie inspection.

import { cookies } from "next/headers";
import Link from "next/link";
import { redirect } from "next/navigation";
import { LoginForm } from "@/components/auth/login-form";
import { AlertDescription, AlertSuccess } from "@/components/ui/alert";
import { AUTH_COOKIE_NAME } from "@/lib/auth";
import { isJwtExpired } from "@/lib/jwt";

type LoginSearchParams = {
  next?: string;
  reset?: string;
};

type LoginPageProps = {
  searchParams?: LoginSearchParams | Promise<LoginSearchParams>;
};

export default async function LoginPage(props: LoginPageProps) {
  const searchParams = await props.searchParams;
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value;
  const shouldShowResetSuccess = searchParams?.reset === "success";

  if (token && !isJwtExpired(token)) {
    redirect(searchParams?.next && searchParams.next !== "/login" ? searchParams.next : "/");
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-muted/40 px-6 py-12">
      <div className="w-full max-w-sm rounded-xl border border-border bg-background p-8 shadow-lg">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-semibold">G-Trac</h1>
          <p className="text-sm text-muted-foreground">Sign in to your account</p>
        </div>
        {shouldShowResetSuccess ? (
          <AlertSuccess className="mb-6">
            <AlertDescription>
              Your password has been updated. You can now sign in with your new password.
            </AlertDescription>
          </AlertSuccess>
        ) : null}
        <LoginForm redirectTo={searchParams?.next ?? null} />
        <div className="mt-4 text-center text-sm">
          <Link
            href="/forgot-password"
            className="text-muted-foreground hover:underline hover:text-accent-foreground"
          >
            Forgot your password?
          </Link>
        </div>
        <div className="text-muted-foreground text-sm text-center mt-4">
          Need an account? Please email{" "}
          <a
            href="mailto:shaun.chuah@glasgow.ac.uk"
            className="hover:underline hover:text-accent-foreground"
          >
            shaun.chuah@glasgow.ac.uk
          </a>
        </div>
      </div>
    </main>
  );
}
