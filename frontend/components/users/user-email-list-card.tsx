// frontend/components/users/user-email-list-card.tsx
// Shows the card that lists all user emails and provides a copy-to-clipboard action.
// Exists to keep the main users table component small while preserving the bulk email copy UI.

"use client";

import { Copy } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { AlertDescription, AlertError } from "@/components/ui/alert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
} from "@/components/ui/input-group";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

import type { ManagementEmails } from "./user-types";

const DEFAULT_TOOLTIP = "Copy to Clipboard";

export function UserEmailListCard() {
  const [emails, setEmails] = useState<ManagementEmails | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tooltipText, setTooltipText] = useState<string>(DEFAULT_TOOLTIP);
  const [tooltipOpen, setTooltipOpen] = useState(false);
  const resetTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadEmails = async () => {
      setError(null);
      try {
        const response = await fetch("/api/dashboard/users?variant=emails", { cache: "no-store" });
        const payload = (await response.json().catch(() => null)) as
          | ManagementEmails
          | { detail?: string }
          | null;

        if (!response.ok) {
          throw new Error(
            (payload as { detail?: string } | null)?.detail ?? "Unable to fetch emails.",
          );
        }

        if (!isMounted) return;
        setEmails(payload as ManagementEmails);
      } catch (err) {
        if (!isMounted) return;
        const message = err instanceof Error ? err.message : "Unable to fetch emails.";
        setError(message);
        setEmails(null);
      }
    };

    void loadEmails();

    return () => {
      isMounted = false;
      if (resetTimerRef.current) {
        clearTimeout(resetTimerRef.current);
      }
    };
  }, []);

  const setTooltipWithReset = (message: string) => {
    setTooltipText(message);
    setTooltipOpen(true);
    if (resetTimerRef.current) {
      clearTimeout(resetTimerRef.current);
    }
    resetTimerRef.current = setTimeout(() => {
      setTooltipText(DEFAULT_TOOLTIP);
      setTooltipOpen(false);
    }, 2000);
  };

  const handleTooltipOpenChange = (open: boolean) => {
    setTooltipOpen(open);
    if (!open) {
      setTooltipText(DEFAULT_TOOLTIP);
      if (resetTimerRef.current) {
        clearTimeout(resetTimerRef.current);
      }
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>User email list</CardTitle>
        <CardDescription>Copy all user emails for bulk messages.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        {error ? (
          <AlertError>
            <AlertDescription>{error}</AlertDescription>
          </AlertError>
        ) : null}
        <InputGroup>
          <InputGroupInput
            readOnly
            value={emails?.emails_joined ?? "Loading emails..."}
            placeholder="Loading emails..."
          />
          <InputGroupAddon align="inline-end">
            <Tooltip open={tooltipOpen} onOpenChange={handleTooltipOpenChange}>
              <TooltipTrigger asChild>
                <InputGroupButton
                  variant="ghost"
                  size="icon-sm"
                  onClick={() => {
                    if (!emails?.emails_joined) return;
                    void navigator.clipboard.writeText(emails.emails_joined).then(
                      () => setTooltipWithReset("Copied!"),
                      () => setTooltipWithReset("Unable to copy"),
                    );
                  }}
                  aria-label="Copy all user emails"
                  disabled={!emails?.emails_joined}
                >
                  <Copy className="h-4 w-4" aria-hidden />
                  <span className="sr-only">Copy emails</span>
                </InputGroupButton>
              </TooltipTrigger>
              <TooltipContent sideOffset={6}>{tooltipText}</TooltipContent>
            </Tooltip>
          </InputGroupAddon>
        </InputGroup>
      </CardContent>
    </Card>
  );
}
