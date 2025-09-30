import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/auth/logout-button";
import { AUTH_COOKIE_NAME } from "@/lib/auth";
import { isJwtExpired } from "@/lib/jwt";

export default async function HomePage() {
  const cookiesStore = await cookies();
  const token = cookiesStore.get(AUTH_COOKIE_NAME)?.value;

  if (!token || isJwtExpired(token)) {
    redirect("/login");
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 bg-muted/40 px-6 py-12">
      <div className="max-w-xl space-y-3 text-center">
        <h1 className="text-3xl font-semibold tracking-tight">Music Samples Frontend</h1>
        <p className="text-base text-muted-foreground">
          This placeholder dashboard confirms that authentication is configured. Replace this content with real
          modules as you migrate features from the Django templates.
        </p>
      </div>
      <LogoutButton />
    </main>
  );
}
