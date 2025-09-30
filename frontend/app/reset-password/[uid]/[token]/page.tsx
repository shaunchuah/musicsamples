// frontend/app/reset-password/[uid]/[token]/page.tsx
// Server component that renders the password reset confirmation flow for tokenised links.
// Provides the SPA entry point reached from password reset emails.

import Link from "next/link";

import { ResetPasswordForm } from "@/components/auth/reset-password-form";

type ResetPasswordPageProps = {
  params: {
    uid: string;
    token: string;
  };
};

export default function ResetPasswordPage({ params }: ResetPasswordPageProps) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-muted/40 px-6 py-12">
      <div className="w-full max-w-sm rounded-xl border border-border bg-background p-8 shadow-lg">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-semibold">Reset password</h1>
          <p className="text-sm text-muted-foreground">
            Enter a new password for your account. This link can only be used once.
          </p>
        </div>
        <ResetPasswordForm uid={params.uid} token={params.token} />
        <div className="text-sm text-center mt-4">
          <Link href="/login" className="underline hover:text-accent-foreground">
            Back to sign in
          </Link>
        </div>
      </div>
    </main>
  );
}
