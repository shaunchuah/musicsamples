// frontend/components/auth/login-form.tsx
// Presents the login UI and wires form submissions to the Next.js authentication API route.
// Lets users sign in from the React SPA while keeping the token in an HTTP-only cookie.

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

type LoginFormProps = {
  redirectTo?: string | null;
};

export function LoginForm({ redirectTo }: LoginFormProps) {
  const router = useRouter();
  const loginSchema = z.object({
    email: z.email("Enter a valid email address."),
    password: z.string().min(8, "Password is required."),
  });

  type LoginFormValues = z.infer<typeof loginSchema>;

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  // memoized so react-hook-form keeps stable submit handler reference across renders
  const onSubmit = useCallback(
    async (values: LoginFormValues) => {
      form.clearErrors("root");

      try {
        const response = await fetch("/api/auth/login", {
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
            message: payload?.error || "Unable to sign in with those credentials.",
          });
          return;
        }

        const target = (() => {
          // Guard against open redirects by only honouring relative paths we issued ourselves.
          if (typeof redirectTo !== "string") {
            return "/";
          }

          const trimmed = redirectTo.trim();
          if (!trimmed || trimmed === "/login") {
            return "/";
          }

          if (!trimmed.startsWith("/") || trimmed.startsWith("//")) {
            return "/";
          }

          return trimmed;
        })();

        router.replace(target);
        router.refresh();
      } catch {
        form.setError("root", {
          message: "Something went wrong. Please try again.",
        });
      }
    },
    [form, redirectTo, router],
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
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  autoComplete="current-password"
                  placeholder="Password"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? "Signing in..." : "Sign in"}
        </Button>
      </form>
    </Form>
  );
}
