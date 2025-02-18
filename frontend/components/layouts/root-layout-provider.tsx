"use client";

import { useSession } from "next-auth/react";
import AuthenticatedLayout from "./authenticated-layout";

// this provider checks if the user is authenticated and
// renders the authenticated layout if they are
// this allows the login page and the reset password page to have no sidebar

function RootLayoutContent({ children }: { children: React.ReactNode }) {
  const { status } = useSession();

  if (status === "authenticated") {
    return <AuthenticatedLayout>{children}</AuthenticatedLayout>;
  }

  return <>{children}</>;
}

export default function RootLayoutProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <RootLayoutContent>{children}</RootLayoutContent>
    </>
  );
}
