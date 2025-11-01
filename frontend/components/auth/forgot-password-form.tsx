// frontend/components/auth/forgot-password-form.tsx
// Renders the forgot-password UI and connects submissions to the Next.js API route.
// Exists so the reset flow behaves like other auth forms with shared validation and feedback patterns.

"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useCallback, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { AlertDescription, AlertError, AlertSuccess } from "@/components/ui/alert";
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

type ForgotPasswordFormValues = {
  email: string;
};

const forgotPasswordSchema = z.object({
  email: z.email("Enter a valid email address."),
});

export function ForgotPasswordForm() {
  const [requestSent, setRequestSent] = useState(false);

  const form = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: "",
    },
  });

  const onSubmit = useCallback(
    async (values: ForgotPasswordFormValues) => {
      setRequestSent(false);
      form.clearErrors("root");

      try {
        const response = await fetch("/api/auth/forgot-password", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(values),
        });

        const payload = (await response.json()) as {
          error?: string;
          success?: boolean;
        };

        if (!response.ok || !payload?.success) {
          form.setError("root", {
            message: payload?.error || "Unable to send password reset instructions.",
          });
          return;
        }

        setRequestSent(true);
      } catch {
        form.setError("root", {
          message: "Something went wrong. Please try again.",
        });
      }
    },
    [form],
  );

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {form.formState.errors.root ? (
          <AlertError>
            <AlertDescription>{form.formState.errors.root.message}</AlertDescription>
          </AlertError>
        ) : null}
        {requestSent ? (
          <AlertSuccess>
            <AlertDescription>
              If an account exists for that email, we have sent a password reset link.
            </AlertDescription>
          </AlertSuccess>
        ) : null}
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" autoComplete="email" placeholder="Email" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" className="w-full" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? "Sending..." : "Send reset link"}
        </Button>
      </form>
    </Form>
  );
}
