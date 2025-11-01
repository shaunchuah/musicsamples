// frontend/components/auth/forgot-password-form.test.tsx
// Exercises the ForgotPasswordForm component to ensure validation, success messaging, and error paths work.
// Exists to give confidence that the reset-request flow correctly talks to the Next.js API route.

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { ForgotPasswordForm } from "@/components/auth/forgot-password-form";

const fetchMock = vi.fn<typeof fetch>();

describe("ForgotPasswordForm", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    globalThis.fetch = fetchMock;
  });

  it("validates the email field before submitting", async () => {
    const user = userEvent.setup();

    render(<ForgotPasswordForm />);

    await user.click(screen.getByRole("button", { name: /send reset link/i }));

    expect(await screen.findByText("Enter a valid email address.")).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("shows a success message when the API request succeeds", async () => {
    const user = userEvent.setup();

    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    } as Response);

    render(<ForgotPasswordForm />);

    await user.type(screen.getByLabelText(/email/i), "user@example.com");
    await user.click(screen.getByRole("button", { name: /send reset link/i }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/auth/forgot-password",
        expect.objectContaining({
          method: "POST",
        }),
      ),
    );

    expect(
      await screen.findByText(
        "If an account exists for that email, we have sent a password reset link.",
      ),
    ).toBeInTheDocument();
  });

  it("surfaces API errors when the request fails", async () => {
    const user = userEvent.setup();

    fetchMock.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: "Unable to send reset email" }),
    } as Response);

    render(<ForgotPasswordForm />);

    await user.type(screen.getByLabelText(/email/i), "user@example.com");
    await user.click(screen.getByRole("button", { name: /send reset link/i }));

    expect(await screen.findByText("Unable to send reset email")).toBeInTheDocument();
  });
});
