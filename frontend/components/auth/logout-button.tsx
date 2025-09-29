// frontend/components/auth/logout-button.tsx
// Renders a button that clears the auth cookie via the logout API route.
// Gives users a visible way to end their session from any protected screen.

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";

export function LogoutButton() {
  const router = useRouter();
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLogout() {
    setIsSigningOut(true);
    setError(null);

    try {
      const response = await fetch("/api/auth/logout", { method: "POST" });

      if (!response.ok) {
        setError("Unable to sign out. Please try again.");
        setIsSigningOut(false);
        return;
      }

      router.replace("/login");
      router.refresh();
    } catch {
      setError("Something went wrong while signing out.");
      setIsSigningOut(false);
    }
  }

  return (
    <div className="space-y-2">
      <Button variant="outline" onClick={handleLogout} disabled={isSigningOut}>
        {isSigningOut ? "Signing out..." : "Sign out"}
      </Button>
      {error ? <p className="text-sm text-destructive">{error}</p> : null}
    </div>
  );
}
