// frontend/app/forgot-password/page.tsx
// Server component that renders the password reset request screen for the SPA.
// Provides a dedicated route where users can request reset emails via the Next.js API.

import Link from "next/link";

import { ForgotPasswordForm } from "@/components/auth/forgot-password-form";

export default function ForgotPasswordPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-muted/40 px-6 py-12">
      <div className="w-full max-w-sm rounded-xl border border-border bg-background p-8 shadow-lg">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-semibold">Forgot password</h1>
          <p className="text-sm text-muted-foreground">
            Enter your email address and we&apos;ll send you a reset link.
          </p>
        </div>
        <ForgotPasswordForm />
        <div className="text-sm text-center mt-4">
          <Link href="/login" className="underline hover:text-accent-foreground">
            Back to sign in
          </Link>
        </div>
      </div>
    </main>
  );
}
