// frontend/components/auth/login-form.test.tsx
// Exercises the LoginForm client component to ensure validation, submission, and routing behaviour work as expected.
// Exists to give confidence that the react-hook-form + shadcn implementation handles success and failure user flows.

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { LoginForm } from "./login-form";

const replaceMock = vi.fn();
const refreshMock = vi.fn();
const fetchMock = vi.fn<typeof fetch>();

vi.mock("next/navigation", () => ({
	useRouter: () => ({
		replace: replaceMock,
		refresh: refreshMock,
	}),
}));

describe("LoginForm", () => {
	beforeEach(() => {
		replaceMock.mockReset();
		refreshMock.mockReset();
		fetchMock.mockReset();
		globalThis.fetch = fetchMock;
	});

	it("shows field validation messages when inputs are missing", async () => {
		const user = userEvent.setup();

		render(<LoginForm />);

		await user.click(screen.getByRole("button", { name: /sign in/i }));

		expect(
			await screen.findByText("Enter a valid email address."),
		).toBeInTheDocument();
		expect(screen.getByText("Password is required.")).toBeInTheDocument();
		expect(fetchMock).not.toHaveBeenCalled();
	});

	it("submits credentials and redirects when authentication succeeds", async () => {
		const user = userEvent.setup();

		fetchMock.mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true }),
		} as Response);

		render(<LoginForm redirectTo="/dashboard" />);

		await user.type(screen.getByLabelText(/email/i), "user@example.com");
		await user.type(screen.getByLabelText(/password/i), "safepassword");
		await user.click(screen.getByRole("button", { name: /sign in/i }));

		await waitFor(() =>
			expect(fetchMock).toHaveBeenCalledWith(
				"/api/auth/login",
				expect.objectContaining({
					method: "POST",
				}),
			),
		);

		expect(fetchMock).toHaveBeenCalledTimes(1);
		expect(replaceMock).toHaveBeenCalledWith("/dashboard");
		expect(refreshMock).toHaveBeenCalled();
	});

	it("surfaces API errors when authentication fails", async () => {
		const user = userEvent.setup();

		fetchMock.mockResolvedValueOnce({
			ok: false,
			json: async () => ({ error: "Invalid credentials" }),
		} as Response);

		render(<LoginForm />);

		await user.type(screen.getByLabelText(/email/i), "user@example.com");
		await user.type(screen.getByLabelText(/password/i), "badpass");
		await user.click(screen.getByRole("button", { name: /sign in/i }));

		expect(await screen.findByText("Invalid credentials")).toBeInTheDocument();
		expect(replaceMock).not.toHaveBeenCalled();
		expect(refreshMock).not.toHaveBeenCalled();
	});
});
