// frontend/components/users/user-form-dialog.tsx
// Renders the create/edit user form dialog with validation and submission handling.
// Exists to keep the users table lean while reusing the same dialog across actions.

import { zodResolver } from "@hookform/resolvers/zod";
import { useCallback, useEffect, useState } from "react";
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
  JOB_TITLE_OPTIONS,
  jobTitleEnum,
  PRIMARY_ORG_OPTIONS,
  primaryOrgEnum,
} from "./user-options";
import type { StaffUser, UserFormValues } from "./user-types";

const dialogSchema = z.object({
  email: z.string().email("Enter a valid email."),
  first_name: z.string().min(1, "First name is required."),
  last_name: z.string().min(1, "Last name is required."),
  job_title: z.union([z.literal(""), jobTitleEnum]),
  primary_organisation: z.union([z.literal(""), primaryOrgEnum]),
});

function normalisePayload(values: UserFormValues): UserFormValues {
  return {
    ...values,
    job_title: values.job_title?.trim() ?? "",
    primary_organisation: values.primary_organisation?.trim() ?? "",
  };
}

type UserFormDialogProps = {
  mode: "create" | "edit";
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultValues: StaffUser | null;
  onSubmit: (values: UserFormValues, userId?: number) => Promise<void>;
};

export function UserFormDialog({
  mode,
  open,
  onOpenChange,
  defaultValues,
  onSubmit,
}: UserFormDialogProps) {
  const [submitError, setSubmitError] = useState<string | null>(null);

  const form = useForm<UserFormValues>({
    resolver: zodResolver(dialogSchema),
    defaultValues: {
      email: "",
      first_name: "",
      last_name: "",
      job_title: "",
      primary_organisation: "",
    },
  });

  useEffect(() => {
    form.reset({
      email: defaultValues?.email ?? "",
      first_name: defaultValues?.first_name ?? "",
      last_name: defaultValues?.last_name ?? "",
      job_title: defaultValues?.job_title ?? "",
      primary_organisation: defaultValues?.primary_organisation ?? "",
    });
    setSubmitError(null);
  }, [defaultValues, form, open]);

  const handleSubmit = useCallback(
    async (values: UserFormValues) => {
      setSubmitError(null);
      try {
        await onSubmit(normalisePayload(values), defaultValues?.id);
        onOpenChange(false);
      } catch (error) {
        const message = error instanceof Error ? error.message : "Unable to save user.";
        setSubmitError(message);
      }
    },
    [defaultValues?.id, onOpenChange, onSubmit],
  );

  const isSubmitting = form.formState.isSubmitting;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{mode === "create" ? "Add New User" : "Edit User"}</DialogTitle>
          <DialogDescription>
            {mode === "create"
              ? "Create a new account for a team member. A welcome email will be sent automatically."
              : "Update the user details shown in the management table."}
          </DialogDescription>
        </DialogHeader>

        {submitError ? (
          <AlertError>
            <AlertDescription>{submitError}</AlertDescription>
          </AlertError>
        ) : null}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      autoComplete="email"
                      placeholder="user@example.com"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

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
                  <FormLabel>Job title</FormLabel>
                  <FormControl>
                    <select
                      name={field.name}
                      value={field.value ?? ""}
                      onChange={(event) => field.onChange(event.target.value)}
                      onBlur={field.onBlur}
                      ref={field.ref}
                      className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      {JOB_TITLE_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
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
                  <FormLabel>Primary organisation</FormLabel>
                  <FormControl>
                    <select
                      name={field.name}
                      value={field.value ?? ""}
                      onChange={(event) => field.onChange(event.target.value)}
                      onBlur={field.onBlur}
                      ref={field.ref}
                      className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      {PRIMARY_ORG_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Saving..." : mode === "create" ? "Create user" : "Save changes"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
