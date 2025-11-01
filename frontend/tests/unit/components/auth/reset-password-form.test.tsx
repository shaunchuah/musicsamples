// frontend/components/auth/reset-password-form.test.tsx
// Exercises the ResetPasswordForm component to check validation, API wiring, and navigation on success.
// Exists to ensure the password reset confirmation flow is reliable from the SPA.

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { ResetPasswordForm } from "@/components/auth/reset-password-form";

const replaceMock = vi.fn();
const fetchMock = vi.fn<typeof fetch>();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    replace: replaceMock,
  }),
}));

describe("ResetPasswordForm", () => {
  beforeEach(() => {
    replaceMock.mockReset();
    fetchMock.mockReset();
    globalThis.fetch = fetchMock;
  });

  it("validates the password field before submitting", async () => {
    const user = userEvent.setup();

    render(<ResetPasswordForm uid="uid123" token="token456" />);

    await user.click(screen.getByRole("button", { name: /reset password/i }));

    expect(await screen.findByText("Password must be at least 8 characters.")).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("submits the API request and redirects on success", async () => {
    const user = userEvent.setup();

    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    } as Response);

    render(<ResetPasswordForm uid="uid123" token="token456" />);

    await user.type(screen.getByLabelText(/new password/i), "newpassword1");
    await user.click(screen.getByRole("button", { name: /reset password/i }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/auth/reset-password",
        expect.objectContaining({
          method: "POST",
        }),
      ),
    );

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(replaceMock).toHaveBeenCalledWith("/login?reset=success");
  });

  it("displays API errors when the backend returns a failure", async () => {
    const user = userEvent.setup();

    fetchMock.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: "Token invalid" }),
    } as Response);

    render(<ResetPasswordForm uid="uid123" token="token456" />);

    await user.type(screen.getByLabelText(/new password/i), "newpassword1");
    await user.click(screen.getByRole("button", { name: /reset password/i }));

    expect(await screen.findByText("Token invalid")).toBeInTheDocument();
    expect(replaceMock).not.toHaveBeenCalled();
  });
});
