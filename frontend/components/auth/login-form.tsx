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

type LoginFormProps = {
	redirectTo?: string | null;
};

export function LoginForm({ redirectTo }: LoginFormProps) {
	const router = useRouter();
	const loginSchema = z.object({
		email: z.string().email("Enter a valid email address."),
		password: z.string().min(1, "Password is required."),
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
						message:
							payload?.error || "Unable to sign in with those credentials.",
					});
					return;
				}

				const target = redirectTo && redirectTo !== "/login" ? redirectTo : "/";
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
									placeholder="Email"
									{...field}
								/>
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
				{form.formState.errors.root ? (
					<p
						className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive"
						role="alert"
					>
						{form.formState.errors.root.message}
					</p>
				) : null}
				<Button
					type="submit"
					className="w-full"
					disabled={form.formState.isSubmitting}
				>
					{form.formState.isSubmitting ? "Signing in..." : "Sign in"}
				</Button>
			</form>
			<div className="text-muted-foreground text-sm text-center mt-4">
				Need an account? Please email{" "}
				<a
					href="mailto:shaun.chuah@glasgow.ac.uk"
					className="underline hover:text-accent-foreground"
				>
					shaun.chuah@glasgow.ac.uk
				</a>
			</div>
		</Form>
	);
}
