// frontend/components/auth/change-password-dialog.tsx
// Renders a dialog that lets authenticated users set a new password from the dashboard.
// Exists to keep the password change modal logic reusable and separate from navigation UI.

"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useCallback, useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { AlertDescription, AlertError, AlertSuccess } from "@/components/ui/alert";
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

const changePasswordSchema = z
  .object({
    newPassword: z.string().min(8, "Password must be at least 8 characters."),
    confirmPassword: z.string().min(1, "Please confirm your new password."),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords do not match.",
    path: ["confirmPassword"],
  });

type ChangePasswordFormValues = z.infer<typeof changePasswordSchema>;

type ChangePasswordDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function ChangePasswordDialog({ open, onOpenChange }: ChangePasswordDialogProps) {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);

  const form = useForm<ChangePasswordFormValues>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      newPassword: "",
      confirmPassword: "",
    },
  });

  useEffect(() => {
    if (open) {
      form.reset({ newPassword: "", confirmPassword: "" });
      setSubmitError(null);
      setSubmitSuccess(null);
    }
  }, [form, open]);

  const handleSubmit = useCallback(
    async (values: ChangePasswordFormValues) => {
      setSubmitError(null);
      setSubmitSuccess(null);

      try {
        const response = await fetch("/api/auth/change-password", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            newPassword: values.newPassword,
            confirmPassword: values.confirmPassword,
          }),
        });

        const payload = (await response.json()) as { error?: string; success?: boolean };

        if (!response.ok || !payload?.success) {
          setSubmitError(payload?.error || "Unable to change password.");
          return;
        }

        form.reset({ newPassword: "", confirmPassword: "" });
        setSubmitSuccess("Password updated.");
      } catch {
        setSubmitError("Something went wrong. Please try again.");
      }
    },
    [form],
  );

  const isSubmitting = form.formState.isSubmitting;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Change password</DialogTitle>
          <DialogDescription>Enter and confirm a new password for your account.</DialogDescription>
        </DialogHeader>

        {submitError ? (
          <AlertError>
            <AlertDescription>{submitError}</AlertDescription>
          </AlertError>
        ) : null}

        {submitSuccess ? (
          <AlertSuccess>
            <AlertDescription>{submitSuccess}</AlertDescription>
          </AlertSuccess>
        ) : null}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="newPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>New password</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      autoComplete="new-password"
                      placeholder="New password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="confirmPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Confirm password</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      autoComplete="new-password"
                      placeholder="Confirm password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Updating..." : "Update password"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
