// frontend/components/auth/reset-password-form.tsx
// Renders the password reset confirmation UI used on the tokenised reset route.
// Exists so users can set a new password from the SPA while leveraging shared form utilities.

"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useCallback } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { AlertDescription, AlertError } from "../ui/alert";

const resetPasswordSchema = z.object({
  password: z.string().min(8, "Password must be at least 8 characters."),
});

type ResetPasswordFormValues = z.infer<typeof resetPasswordSchema>;

type ResetPasswordFormProps = {
  uid: string;
  token: string;
};

export function ResetPasswordForm({ uid, token }: ResetPasswordFormProps) {
  const router = useRouter();

  const form = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      password: "",
    },
  });

  const onSubmit = useCallback(
    async (values: ResetPasswordFormValues) => {
      form.clearErrors("root");

      try {
        const response = await fetch("/api/auth/reset-password", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            uid,
            token,
            newPassword: values.password,
          }),
        });

        const payload = (await response.json()) as {
          error?: string;
          success?: boolean;
        };

        if (!response.ok || !payload?.success) {
          form.setError("root", {
            message: payload?.error || "Unable to reset your password.",
          });
          return;
        }

        router.replace("/login?reset=success");
      } catch {
        form.setError("root", {
          message: "Something went wrong. Please try again.",
        });
      }
    },
    [form, router, token, uid],
  );

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {form.formState.errors.root ? (
          <AlertError>
            <AlertDescription>{form.formState.errors.root.message}</AlertDescription>
          </AlertError>
        ) : null}
        <FormField
          control={form.control}
          name="password"
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
        <Button type="submit" className="w-full" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? "Saving..." : "Reset password"}
        </Button>
      </form>
    </Form>
  );
}
