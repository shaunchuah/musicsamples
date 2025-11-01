import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { AppSidebar } from "@/components/dashboard/app-sidebar";
import type { DashboardUser } from "@/components/dashboard/user-profile-menu";
import { SamplesTable } from "@/components/samples/samples-table";
import {
	Breadcrumb,
	BreadcrumbSeparator,
	BreadcrumbLink,
	BreadcrumbItem,
	BreadcrumbList,
	BreadcrumbPage,
} from "@/components/ui/breadcrumb";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
	SidebarInset,
	SidebarProvider,
	SidebarTrigger,
} from "@/components/ui/sidebar";
import { AUTH_COOKIE_NAME } from "@/lib/auth";
import { isJwtExpired, parseJwt } from "@/lib/jwt";

function resolveDashboardUser(token: string | null | undefined): DashboardUser {
	if (!token) {
		return { email: null, firstName: null, lastName: null };
	}

	const payload = parseJwt(token);
	if (!payload || typeof payload !== "object") {
		return { email: null, firstName: null, lastName: null };
	}

	const email = (() => {
		const value = payload?.email ?? payload?.user_email ?? null;
		return typeof value === "string" ? value : null;
	})();

	const firstName = (() => {
		const value = payload?.first_name ?? payload?.firstName ?? null;
		return typeof value === "string" ? value : null;
	})();

	const lastName = (() => {
		const value = payload?.last_name ?? payload?.lastName ?? null;
		return typeof value === "string" ? value : null;
	})();

	return { email, firstName, lastName };
}

export default async function HomePage() {
	const cookiesStore = await cookies();
	const token = cookiesStore.get(AUTH_COOKIE_NAME)?.value ?? null;

	if (!token || isJwtExpired(token)) {
		redirect("/login");
	}

	const user = resolveDashboardUser(token);

	return (
		<SidebarProvider>
			<div className="flex min-h-screen w-full bg-muted/40">
				<AppSidebar user={user} activeHref="/" />
				<SidebarInset>
					<header className="flex h-16 shrink-0 items-center gap-4 border-b px-4">
						<div className="flex items-center gap-2">
							<SidebarTrigger className="-ml-1" />
							<Separator orientation="vertical" className="h-6" />
							<Breadcrumb>
								<BreadcrumbList>
									<BreadcrumbItem>
										<BreadcrumbLink href="/">Home</BreadcrumbLink>
									</BreadcrumbItem>
									<BreadcrumbSeparator />
									<BreadcrumbItem>
										<BreadcrumbLink href="/">Samples</BreadcrumbLink>
									</BreadcrumbItem>
								</BreadcrumbList>
							</Breadcrumb>
						</div>
					</header>
					<main className="flex flex-1 flex-col gap-6 p-6">
						<section className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
							<Card>
								<CardHeader>
									<CardTitle>Samples Overview</CardTitle>
									<CardDescription>
										Quick snapshot of recent sample activity.
									</CardDescription>
								</CardHeader>
								<CardContent>
									<p className="text-sm text-muted-foreground">
										Surface a count of active samples, pending uploads, or other
										high-value metrics here.
									</p>
								</CardContent>
							</Card>
							<Card>
								<CardHeader>
									<CardTitle>Box Tracking</CardTitle>
									<CardDescription>
										Monitor box movements across the lab.
									</CardDescription>
								</CardHeader>
								<CardContent>
									<p className="text-sm text-muted-foreground">
										Highlight the latest experiments or flag boxes that need
										follow-up.
									</p>
								</CardContent>
							</Card>
							<Card className="md:col-span-2 xl:col-span-1">
								<CardHeader>
									<CardTitle>Datasets</CardTitle>
									<CardDescription>
										Track dataset refresh cadence and ownership.
									</CardDescription>
								</CardHeader>
								<CardContent>
									<p className="text-sm text-muted-foreground">
										Use this slot for quick access to dataset automation or
										quality checks.
									</p>
								</CardContent>
							</Card>
						</section>
						<Card>
							<CardHeader>
								<CardTitle>Recent Samples</CardTitle>
								<CardDescription>
									Live data pulled directly from the api/v3 samples endpoint.
								</CardDescription>
							</CardHeader>
							<CardContent>
								<SamplesTable />
							</CardContent>
						</Card>
					</main>
				</SidebarInset>
			</div>
		</SidebarProvider>
	);
}
