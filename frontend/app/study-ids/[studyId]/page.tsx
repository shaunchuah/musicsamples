// frontend/app/study-ids/[studyId]/page.tsx
// Renders the standalone study identifier detail page as part of the dashboard shell.
// Exists so the Study ID “View” action opens a dedicated page like the sample detail view instead of a modal.

import { cookies } from "next/headers";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import type { ReactNode } from "react";

import { AppSidebar } from "@/components/dashboard/app-sidebar";
import { StudyIdEditDialog } from "@/components/study-ids/study-id-edit-dialog";
import { StudyIdFilesCard } from "@/components/study-ids/study-id-files-card";
import { StudyIdSamplesCard } from "@/components/study-ids/study-id-samples-card";
import {
	Breadcrumb,
	BreadcrumbItem,
	BreadcrumbLink,
	BreadcrumbList,
	BreadcrumbPage,
	BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import DetailHeader from "@/components/ui/detail-header";
import {
	SidebarInset,
	SidebarProvider,
	SidebarTrigger,
} from "@/components/ui/sidebar";
import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";
import { resolveDashboardUser } from "@/lib/dashboard-user";
import { isJwtExpired } from "@/lib/jwt";

type StudyIdHistoryChange = {
	field: string;
	old: string | null;
	new: string | null;
};

type StudyIdHistoryEntry = {
	history_date: string;
	history_user: string | null;
	changes: StudyIdHistoryChange[];
};

type StudyIdDetailResponse = {
	id: number;
	name: string;
	study_name: string | null;
	study_name_label: string | null;
	study_group: string | null;
	study_group_label: string | null;
	age: number | null;
	sex: string | null;
	sex_label: string | null;
	study_center: string | null;
	study_center_label: string | null;
	genotype_data_available: boolean | null;
	nod2_mutation_present: boolean | null;
	il23r_mutation_present: boolean | null;
	sample_count: number;
	file_count: number;
	history: StudyIdHistoryEntry[];
};

type PageParams = {
	studyId: string;
};

type DetailRow = {
	label: string;
	value: string;
};

const datetimeFormatter = new Intl.DateTimeFormat("en-GB", {
	year: "numeric",
	month: "short",
	day: "2-digit",
	hour: "2-digit",
	minute: "2-digit",
});

function formatBoolean(value: boolean | null | undefined) {
	if (value === true) {
		return "Yes";
	}
	if (value === false) {
		return "No";
	}
	return "-";
}

function formatDateTime(value: string | null) {
	if (!value) {
		return "-";
	}
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) {
		return value;
	}
	return datetimeFormatter.format(date);
}

function formatMaybe(value: string | null | undefined, fallback = "-") {
	if (value === null || value === undefined || value === "") {
		return fallback;
	}
	return value;
}

async function resolveStudyIdentifierId(
	name: string,
	token: string,
): Promise<number | null> {
	const response = await fetch(
		buildBackendUrl(
			`/api/v3/study-ids/search/?query=${encodeURIComponent(name)}&page_size=5`,
		),
		{
			headers: {
				Authorization: `Bearer ${token}`,
				"Content-Type": "application/json",
			},
			cache: "no-store",
		},
	);

	if (!response.ok) {
		throw new Error("Failed to resolve study ID.");
	}

	const payload = await response.json().catch(() => null);
	const results = Array.isArray(payload?.results) ? payload.results : payload;
	if (!Array.isArray(results)) {
		return null;
	}

	const normalized = name.trim().toLowerCase();
	const match = results.find(
		(entry: { id: number; name?: string }) =>
			entry.name?.toLowerCase() === normalized,
	);

	return match ? match.id : null;
}

async function fetchStudyIdDetailById(
	studyId: number,
	token: string,
): Promise<StudyIdDetailResponse> {
	const response = await fetch(
		buildBackendUrl(`/api/v3/study-ids/${studyId}/`),
		{
			headers: {
				Authorization: `Bearer ${token}`,
				"Content-Type": "application/json",
			},
			cache: "no-store",
		},
	);

	if (!response.ok) {
		throw new Error("Failed to load study ID details.");
	}

	return (await response.json()) as StudyIdDetailResponse;
}

function buildMetadataRows(detail: StudyIdDetailResponse): DetailRow[] {
	return [
		{
			label: "Study ID",
			value: detail.name,
		},
		{
			label: "Study name",
			value: formatMaybe(detail.study_name_label ?? detail.study_name),
		},
		{
			label: "Study group",
			value: formatMaybe(detail.study_group_label ?? detail.study_group),
		},
		{
			label: "Age",
			value: detail.age === null ? "-" : String(detail.age),
		},
		{
			label: "Sex",
			value: formatMaybe(detail.sex_label ?? detail.sex),
		},
		{
			label: "Center",
			value: formatMaybe(detail.study_center_label ?? detail.study_center),
		},
		{
			label: "Genotyping available",
			value: formatBoolean(detail.genotype_data_available),
		},
		{
			label: "NOD2 mutation present",
			value: formatBoolean(detail.nod2_mutation_present),
		},
		{
			label: "IL23R mutation present",
			value: formatBoolean(detail.il23r_mutation_present),
		},
		{
			label: "Samples linked",
			value: `${detail.sample_count} sample(s)`,
		},
		{
			label: "Files linked",
			value: `${detail.file_count} file(s)`,
		},
	];
}

function HistoryList({ history }: { history: StudyIdHistoryEntry[] }) {
	if (!history.length) {
		return (
			<p className="text-sm text-muted-foreground">No history recorded yet.</p>
		);
	}

	return (
		<div className="space-y-3">
			{history.map((entry) => (
				<div
					key={entry.history_date}
					className="rounded-md border border-border/60 bg-muted/50 px-3 py-2 text-sm"
				>
					<p className="text-[0.7rem] text-muted-foreground">
						{formatDateTime(entry.history_date)} ·{" "}
						{entry.history_user ?? "Unknown user"}
					</p>
					{entry.changes.length ? (
						<ul className="mt-2 space-y-1">
							{entry.changes.map((change) => (
								<li key={`${entry.history_date}-${change.field}`}>
									<span className="font-semibold">
										{change.field.replace(/_/g, " ")}
									</span>{" "}
									changed from{" "}
									<span className="font-semibold">
										{change.old ?? "blank field"}
									</span>{" "}
									to{" "}
									<span className="font-semibold">
										{change.new ?? "blank field"}
									</span>
								</li>
							))}
						</ul>
					) : (
						<p className="mt-2 text-sm text-muted-foreground">
							No fields changed.
						</p>
					)}
				</div>
			))}
		</div>
	);
}

function DetailCard({
	title,
	rows,
	actions,
}: {
	title: string;
	rows: DetailRow[];
	actions?: ReactNode;
}) {
	return (
		<Card>
			<CardHeader>
				<CardTitle>{title}</CardTitle>
			</CardHeader>
			<CardContent className="overflow-hidden">
				<table className="w-full table-auto border-collapse text-sm mb-4">
					<tbody>
						{rows.map((row) => (
							<tr
								key={row.label}
								className="border-b border-border/40 last:border-none"
							>
								<th className="w-1/3 px-2 py-2 text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground">
									{row.label}
								</th>
								<td className="px-2 py-2">{row.value}</td>
							</tr>
						))}
					</tbody>
				</table>
				{actions ?? (
					<Button asChild size="sm">
						<Link href={`/study_id/edit/`}>Edit</Link>
					</Button>
				)}
			</CardContent>
		</Card>
	);
}

export default async function StudyIdDetailPage({
	params,
}: {
	params: PageParams;
}) {
	const cookiesStore = await cookies();
	const token = cookiesStore.get(AUTH_COOKIE_NAME)?.value ?? null;

	if (!token || isJwtExpired(token)) {
		redirect("/login");
	}

	const user = resolveDashboardUser(token);
	const resolvedId = await resolveStudyIdentifierId(params.studyId, token);
	if (!resolvedId) {
		notFound();
	}
	const detail = await fetchStudyIdDetailById(resolvedId, token);

	return (
		<SidebarProvider>
			<div className="flex min-h-screen w-full bg-muted/40">
				<AppSidebar user={user} activeHref="/study-ids" />
				<SidebarInset className="min-w-0">
					<header className="sticky top-0 z-20 flex h-16 shrink-0 items-center gap-4 border-b bg-muted/40 px-4 backdrop-blur supports-[backdrop-filter]:bg-muted/60">
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
										<BreadcrumbLink href="/study-ids">Study IDs</BreadcrumbLink>
									</BreadcrumbItem>
									<BreadcrumbSeparator />
									<BreadcrumbItem>
										<BreadcrumbPage>{detail.name}</BreadcrumbPage>
									</BreadcrumbItem>
								</BreadcrumbList>
							</Breadcrumb>
						</div>
					</header>
					<main className="flex flex-1 flex-col gap-6 p-6">
						<Link href="/study-ids" className="text-sm text-primary underline">
							← Back to Study IDs
						</Link>
						<DetailHeader category="Study Identifier" title={detail.name} />
						<section className="grid gap-6 lg:grid-cols-3">
							<div className="lg:col-span-2 space-y-6">
								<DetailCard
									title="Details"
									rows={buildMetadataRows(detail)}
									actions={
										<StudyIdEditDialog
											studyId={{
												id: detail.id,
												name: detail.name,
												study_name: detail.study_name,
											}}
											refreshOnSave
											triggerLabel="Edit"
										/>
									}
								/>
								<StudyIdSamplesCard studyIdName={detail.name} />
								<StudyIdFilesCard studyId={detail.id} />
							</div>
							<div className="lg:col-span-1 space-y-6">
								<Card>
									<CardHeader>
										<CardTitle>History</CardTitle>
									</CardHeader>
									<CardContent>
										<HistoryList history={detail.history} />
									</CardContent>
								</Card>
							</div>
						</section>
					</main>
				</SidebarInset>
			</div>
		</SidebarProvider>
	);
}
