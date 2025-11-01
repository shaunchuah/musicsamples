// frontend/components/dashboard/user-profile-menu.tsx
// Displays the active user's identity summary and related account actions in the sidebar footer.
// Exists so every dashboard screen can re-use the same profile dropdown without duplicating logout logic.

"use client";

import { ChevronDownIcon } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

export type DashboardUser = {
  firstName?: string | null;
  lastName?: string | null;
  email?: string | null;
};

type UserProfileMenuProps = {
  user: DashboardUser;
};

function getInitials({ firstName, lastName, email }: DashboardUser): string {
  const fallback = email?.trim()?.[0];
  const firstInitial = firstName?.trim()?.[0];
  const lastInitial = lastName?.trim()?.[0];

  const initials = [firstInitial, lastInitial].filter(Boolean).join("");
  return initials || (fallback ? fallback.toUpperCase() : "?");
}

function getFullName({ firstName, lastName }: DashboardUser): string {
  const parts = [firstName?.trim(), lastName?.trim()].filter(Boolean);
  return parts.length > 0 ? parts.join(" ") : "Unnamed User";
}

export function UserProfileMenu({ user }: UserProfileMenuProps) {
  const router = useRouter();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  const handleLogout = useCallback(async () => {
    setIsLoggingOut(true);
    try {
      const response = await fetch("/api/auth/logout", { method: "POST" });
      if (!response.ok) {
        setIsLoggingOut(false);
        return;
      }
      setIsOpen(false);
      router.replace("/login");
      router.refresh();
    } catch {
      setIsLoggingOut(false);
    }
  }, [router]);

  return (
    <div ref={containerRef} className="relative flex w-full flex-col gap-2">
      <button
        type="button"
        onClick={() => setIsOpen((previous) => !previous)}
        aria-expanded={isOpen}
        aria-haspopup="menu"
        className="border-border bg-background/60 hover:bg-muted/80 focus-visible:ring-ring/60 focus-visible:outline-none focus-visible:ring-2 flex w-full items-center justify-between rounded-md border p-2 text-left transition"
      >
        <div className="flex items-center gap-3">
          <div className="bg-primary/10 text-primary flex size-10 items-center justify-center rounded-full text-sm font-medium">
            {getInitials(user)}
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium">{getFullName(user)}</p>
            <p className="truncate text-xs text-muted-foreground">
              {user.email ?? "user@example.com"}
            </p>
          </div>
        </div>
        <ChevronDownIcon
          className={`size-4 transition-transform ${isOpen ? "rotate-180" : "rotate-0"}`}
        />
      </button>
      {isOpen ? (
        <div
          role="menu"
          className="bg-popover text-popover-foreground border-border absolute bottom-full left-0 right-0 z-50 mb-2 rounded-md border p-2 shadow-lg"
        >
          <div className="rounded-md bg-muted/50 px-3 py-2 text-xs">
            <p className="font-semibold text-foreground">{getFullName(user)}</p>
            <p className="mt-0.5 truncate text-muted-foreground">
              {user.email ?? "user@example.com"}
            </p>
          </div>
          <div className="mt-2 flex flex-col gap-1">
            <Link
              href="/profile"
              onClick={() => setIsOpen(false)}
              className="hover:bg-muted/80 focus-visible:ring-ring/60 rounded-md px-2 py-1.5 text-sm transition focus-visible:outline-none focus-visible:ring-2"
            >
              Profile
            </Link>
            <Link
              href="/change-password"
              onClick={() => setIsOpen(false)}
              className="hover:bg-muted/80 focus-visible:ring-ring/60 rounded-md px-2 py-1.5 text-sm transition focus-visible:outline-none focus-visible:ring-2"
            >
              Change Password
            </Link>
            <button
              type="button"
              onClick={() => {
                if (!isLoggingOut) {
                  void handleLogout();
                }
              }}
              className="hover:bg-destructive/10 focus-visible:ring-destructive/60 rounded-md px-2 py-1.5 text-left text-sm text-destructive transition focus-visible:outline-none focus-visible:ring-2"
            >
              {isLoggingOut ? "Signing out..." : "Logout"}
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
