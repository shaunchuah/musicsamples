// frontend/tests/unit/components/users/users-table.test.tsx
// Covers the UsersTable client component to ensure it renders API data and flows through the create dialog.
// Exists to give confidence that staff user management works in the Next.js dashboard without manual QA.

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { UsersTable } from "@/components/users/users-table";

const fetchMock = vi.fn<typeof fetch>();

describe("UsersTable", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    globalThis.fetch = fetchMock;
  });

  it("renders user rows after loading", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        results: [
          {
            id: 1,
            email: "user@example.com",
            first_name: "Ada",
            last_name: "Lovelace",
            job_title: null,
            primary_organisation: null,
            is_staff: true,
            is_active: true,
            last_login: null,
            date_joined: "2024-01-01T00:00:00Z",
          },
        ],
        count: 1,
      }),
    } as Response);

    render(<UsersTable />);

    expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();
    expect(screen.getByText("user@example.com")).toBeInTheDocument();

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/dashboard/users",
      expect.objectContaining({ cache: "no-store" }),
    );
  });

  it("creates a user through the dialog and refreshes the list", async () => {
    const user = userEvent.setup();

    // Initial load returns no users
    fetchMock.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ results: [], count: 0 }),
    } as Response);

    // Create call succeeds
    fetchMock.mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => ({ id: 2 }),
    } as Response);

    // Reload shows the new user
    fetchMock.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        results: [
          {
            id: 2,
            email: "new.user@example.com",
            first_name: "New",
            last_name: "User",
            job_title: "Researcher",
            primary_organisation: "G-Trac",
            is_staff: false,
            is_active: true,
            last_login: null,
            date_joined: "2024-02-01T00:00:00Z",
          },
        ],
        count: 1,
      }),
    } as Response);

    render(<UsersTable />);

    expect(await screen.findByText(/Total Count/i)).toHaveTextContent("0");

    await user.click(screen.getByRole("button", { name: /add new user/i }));
    await user.type(screen.getByLabelText(/email/i), "new.user@example.com");
    await user.type(screen.getByLabelText(/first name/i), "New");
    await user.type(screen.getByLabelText(/last name/i), "User");
    await user.type(screen.getByLabelText(/job title/i), "Researcher");
    await user.type(screen.getByLabelText(/primary organisation/i), "G-Trac");

    await user.click(screen.getByRole("button", { name: /create user/i }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/dashboard/users",
        expect.objectContaining({ method: "POST" }),
      );
    });

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3));
    const nameMatches = await screen.findAllByText(/new user/i);
    expect(nameMatches.length).toBeGreaterThan(0);
    expect(screen.getByText("new.user@example.com")).toBeInTheDocument();
  });

  it("handles non-paginated array responses", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => [
        {
          id: 3,
          email: "array.user@example.com",
          first_name: "Array",
          last_name: "User",
          job_title: null,
          primary_organisation: null,
          is_staff: false,
          is_active: true,
          last_login: null,
          date_joined: "2024-03-01T00:00:00Z",
        },
      ],
    } as Response);

    render(<UsersTable />);

    expect(await screen.findByText("Array User")).toBeInTheDocument();
    expect(screen.getByText("array.user@example.com")).toBeInTheDocument();
  });
});
