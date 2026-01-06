// frontend/components/auth/account-settings-dialog.tsx
// Renders a dialog that lets authenticated users edit their profile details.
// Exists to keep account editing UI separate from the sidebar menu logic.

"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useCallback, useEffect, useId, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { AlertDescription, AlertError } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  JOB_TITLE_OPTIONS,
  jobTitleEnum,
  PRIMARY_ORG_OPTIONS,
  primaryOrgEnum,
} from "@/components/users/user-options";

const accountSchema = z.object({
  first_name: z.string().min(1, "First name is required."),
  last_name: z.string().min(1, "Last name is required."),
  job_title: z.union([z.literal(""), jobTitleEnum]),
  primary_organisation: z.union([z.literal(""), primaryOrgEnum]),
});

const EMPTY_SELECT_VALUE = "__none__";

type AccountFormValues = z.infer<typeof accountSchema>;

type AccountSettingsDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onProfileUpdated?: (profile: UserProfileResponse) => void;
};

type UserProfileResponse = {
  first_name?: string | null;
  last_name?: string | null;
  job_title?: string | null;
  primary_organisation?: string | null;
};

function normaliseProfileValue(value: unknown): string {
  return typeof value === "string" ? value : "";
}

export function AccountSettingsDialog({
  open,
  onOpenChange,
  onProfileUpdated,
}: AccountSettingsDialogProps) {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);
  const jobTitleId = useId();
  const primaryOrgId = useId();

  const form = useForm<AccountFormValues>({
    resolver: zodResolver(accountSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      job_title: "",
      primary_organisation: "",
    },
  });

  useEffect(() => {
    if (!open) {
      return;
    }

    let isActive = true;

    async function fetchProfile() {
      setIsLoadingProfile(true);
      setSubmitError(null);
      try {
        const response = await fetch("/api/dashboard/user", { cache: "no-store" });
        if (!response.ok) {
          if (isActive) {
            setSubmitError("Unable to load your profile.");
          }
          return;
        }
        const payload = (await response.json()) as UserProfileResponse;
        if (!isActive) {
          return;
        }
        form.reset({
          first_name: normaliseProfileValue(payload.first_name),
          last_name: normaliseProfileValue(payload.last_name),
          job_title: normaliseProfileValue(payload.job_title),
          primary_organisation: normaliseProfileValue(payload.primary_organisation),
        });
      } catch {
        if (isActive) {
          setSubmitError("Unable to load your profile.");
        }
      } finally {
        if (isActive) {
          setIsLoadingProfile(false);
        }
      }
    }

    void fetchProfile();
    return () => {
      isActive = false;
    };
  }, [form, open]);

  const handleSubmit = useCallback(
    async (values: AccountFormValues) => {
      setSubmitError(null);

      try {
        const response = await fetch("/api/dashboard/user", {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(values),
        });

        const payload = (await response.json()) as UserProfileResponse & { detail?: string };

        if (!response.ok) {
          setSubmitError(payload?.detail || "Unable to update your profile.");
          return;
        }

        onProfileUpdated?.(payload);
        onOpenChange(false);
      } catch {
        setSubmitError("Something went wrong. Please try again.");
      }
    },
    [onOpenChange, onProfileUpdated],
  );

  const isSubmitting = form.formState.isSubmitting;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Account</DialogTitle>
          <DialogDescription>Update your name and organisation details.</DialogDescription>
        </DialogHeader>

        {submitError ? (
          <AlertError>
            <AlertDescription>{submitError}</AlertDescription>
          </AlertError>
        ) : null}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>First name</FormLabel>
                    <FormControl>
                      <Input autoComplete="given-name" placeholder="First name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="last_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Last name</FormLabel>
                    <FormControl>
                      <Input autoComplete="family-name" placeholder="Last name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="job_title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel htmlFor={jobTitleId}>Job title</FormLabel>
                  <FormControl>
                    <Select
                      value={field.value || EMPTY_SELECT_VALUE}
                      onValueChange={(value) =>
                        field.onChange(value === EMPTY_SELECT_VALUE ? "" : value)
                      }
                    >
                      <SelectTrigger id={jobTitleId} className="w-full">
                        <SelectValue
                          placeholder={JOB_TITLE_OPTIONS[0]?.label ?? "Select job title"}
                        />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={EMPTY_SELECT_VALUE}>
                          {JOB_TITLE_OPTIONS[0]?.label ?? "Select job title"}
                        </SelectItem>
                        {JOB_TITLE_OPTIONS.filter((option) => option.value).map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="primary_organisation"
              render={({ field }) => (
                <FormItem>
                  <FormLabel htmlFor={primaryOrgId}>Primary organisation</FormLabel>
                  <FormControl>
                    <Select
                      value={field.value || EMPTY_SELECT_VALUE}
                      onValueChange={(value) =>
                        field.onChange(value === EMPTY_SELECT_VALUE ? "" : value)
                      }
                    >
                      <SelectTrigger id={primaryOrgId} className="w-full">
                        <SelectValue
                          placeholder={
                            PRIMARY_ORG_OPTIONS[0]?.label ?? "Select primary organisation"
                          }
                        />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={EMPTY_SELECT_VALUE}>
                          {PRIMARY_ORG_OPTIONS[0]?.label ?? "Select primary organisation"}
                        </SelectItem>
                        {PRIMARY_ORG_OPTIONS.filter((option) => option.value).map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="submit" disabled={isSubmitting || isLoadingProfile}>
                {isSubmitting ? "Saving..." : "Save changes"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
