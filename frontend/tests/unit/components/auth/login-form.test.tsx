// frontend/components/auth/login-form.test.tsx
// Exercises the LoginForm client component to ensure validation, submission, and routing behaviour work as expected.
// Exists to give confidence that the react-hook-form + shadcn implementation handles success and failure user flows.

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { LoginForm } from "@/components/auth/login-form";
import { DashboardUserProvider } from "@/components/dashboard/user-profile-provider";

const replaceMock = vi.fn();
const refreshMock = vi.fn();
const fetchMock = vi.fn<typeof fetch>();

function resolveRequestUrl(input: RequestInfo | URL): string {
  if (typeof input === "string") {
    return input;
  }
  if (input instanceof URL) {
    return input.toString();
  }
  return input.url;
}

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
    fetchMock.mockImplementation(async (input) => {
      const url = resolveRequestUrl(input);
      if (url === "/api/dashboard/user") {
        return {
          ok: true,
          json: async () => ({}),
        } as Response;
      }
      throw new Error(`Unhandled fetch: ${url}`);
    });
    globalThis.fetch = fetchMock;
  });

  it("shows field validation messages when inputs are missing", async () => {
    const user = userEvent.setup();

    render(
      <DashboardUserProvider>
        <LoginForm />
      </DashboardUserProvider>,
    );

    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText("Enter a valid email address.")).toBeInTheDocument();
    expect(screen.getByText("Password is required.")).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalledWith("/api/auth/login", expect.anything());
  });

  it("submits credentials and redirects when authentication succeeds", async () => {
    const user = userEvent.setup();

    fetchMock.mockImplementation(async (input) => {
      const url = resolveRequestUrl(input);
      if (url === "/api/auth/login") {
        return {
          ok: true,
          json: async () => ({ success: true }),
        } as Response;
      }
      if (url === "/api/dashboard/user") {
        return {
          ok: true,
          json: async () => ({
            email: "user@example.com",
            first_name: "Test",
            last_name: "User",
            is_staff: false,
            is_superuser: false,
            groups: [],
          }),
        } as Response;
      }
      throw new Error(`Unhandled fetch: ${url}`);
    });

    render(
      <DashboardUserProvider>
        <LoginForm redirectTo="/dashboard" />
      </DashboardUserProvider>,
    );

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

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/dashboard/user",
      expect.objectContaining({ cache: "no-store" }),
    );
    expect(replaceMock).toHaveBeenCalledWith("/dashboard");
    expect(refreshMock).toHaveBeenCalled();
  });

  it("surfaces API errors when authentication fails", async () => {
    const user = userEvent.setup();

    fetchMock.mockImplementation(async (input) => {
      const url = resolveRequestUrl(input);
      if (url === "/api/auth/login") {
        return {
          ok: false,
          json: async () => ({ error: "Invalid credentials" }),
        } as Response;
      }
      if (url === "/api/dashboard/user") {
        return {
          ok: true,
          json: async () => ({}),
        } as Response;
      }
      throw new Error(`Unhandled fetch: ${url}`);
    });

    render(
      <DashboardUserProvider>
        <LoginForm />
      </DashboardUserProvider>,
    );

    await user.type(screen.getByLabelText(/email/i), "user@example.com");
    await user.type(screen.getByLabelText(/password/i), "badpass1");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText("Invalid credentials")).toBeInTheDocument();
    expect(replaceMock).not.toHaveBeenCalled();
    expect(refreshMock).not.toHaveBeenCalled();
  });
});
