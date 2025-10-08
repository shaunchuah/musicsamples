// frontend/app/api/dashboard/samples/export/route.ts
// Exposes a Next.js API endpoint to download all sample records as a CSV file.
// Provides a modern replacement for the legacy Django CSV export, gathering paginated API data server-side.

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, buildBackendUrl } from "@/lib/auth";

type StudyIdentifierSummary = {
  id: number;
  name: string;
};

type SampleRow = {
  id: number;
  sample_id: string;
  study_name: string;
  study_name_label: string | null;
  study_identifier: StudyIdentifierSummary | null;
  sample_location: string;
  sample_sublocation: string | null;
  sample_type: string;
  sample_type_label: string | null;
  sample_datetime: string | null;
  timepoint_label: string | null;
  study_group_label: string | null;
  age: number | null;
  sex_label: string | null;
  study_center_label: string | null;
  crp: number | null;
  calprotectin: number | null;
  endoscopic_mucosal_healing_at_3_6_months: boolean | null;
  endoscopic_mucosal_healing_at_12_months: boolean | null;
  genotype_data_available: boolean | null;
  sample_comments: string | null;
  is_used: boolean;
};

type SampleApiPayload = {
  count?: number;
  next?: string | null;
  results?: SampleRow[];
};

const SAMPLES_ENDPOINT = "/api/v3/samples/";
const PAGE_SIZE = 1000;
const MAX_PAGES = 500;

const CSV_COLUMNS: ReadonlyArray<{
  key: keyof SampleRow | "study_identifier_name";
  header: string;
}> = [
  { key: "study_name", header: "Study" },
  { key: "sample_id", header: "Sample ID" },
  { key: "study_identifier_name", header: "Study ID" },
  { key: "sample_location", header: "Location" },
  { key: "sample_sublocation", header: "Sublocation" },
  { key: "sample_type", header: "Sample Type" },
  { key: "sample_datetime", header: "Collected At" },
  { key: "timepoint_label", header: "Timepoint" },
  { key: "study_group_label", header: "Group" },
  { key: "age", header: "Age" },
  { key: "sex_label", header: "Sex" },
  { key: "study_center_label", header: "Center" },
  { key: "crp", header: "CRP" },
  { key: "calprotectin", header: "Calprotectin" },
  {
    key: "endoscopic_mucosal_healing_at_3_6_months",
    header: "Mucosal Healing (3-6m)",
  },
  {
    key: "endoscopic_mucosal_healing_at_12_months",
    header: "Mucosal Healing (12m)",
  },
  { key: "genotype_data_available", header: "Genotyping" },
  { key: "sample_comments", header: "Comments" },
  { key: "is_used", header: "Used" },
];

function formatBoolean(value: boolean | null | undefined): string {
  if (value === null || value === undefined) {
    return "";
  }
  return value ? "Yes" : "";
}

function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "";
  }
  return String(value);
}

function formatDate(value: string | null | undefined): string {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toISOString();
}

function getCsvValue(row: SampleRow, key: (typeof CSV_COLUMNS)[number]["key"]): string {
  if (key === "study_identifier_name") {
    return row.study_identifier?.name ?? "";
  }

  if (key === "study_name") {
    return row.study_name_label ?? row.study_name ?? "";
  }

  if (key === "sample_type") {
    return row.sample_type_label ?? row.sample_type ?? "";
  }

  const value = row[key];

  if (typeof value === "boolean" || key === "is_used" || key.startsWith("endoscopic_mucosal_healing")) {
    return formatBoolean(value as boolean | null | undefined);
  }

  if (typeof value === "number") {
    return formatNumber(value);
  }

  if (key === "sample_datetime") {
    return formatDate(value as string | null | undefined);
  }

  if (value === null || value === undefined) {
    return "";
  }

  return String(value);
}

function escapeCsv(value: string): string {
  if (value.includes('"') || value.includes(",") || value.includes("\n") || value.includes("\r")) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

function buildCsv(rows: SampleRow[]): string {
  const headerLine = CSV_COLUMNS.map((column) => escapeCsv(column.header)).join(",");
  const dataLines = rows.map((row) =>
    CSV_COLUMNS.map((column) => escapeCsv(getCsvValue(row, column.key))).join(","),
  );
  return [headerLine, ...dataLines].join("\n");
}

export async function GET(request: Request): Promise<Response> {
  try {
    const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value ?? null;

    if (!token) {
      return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
    }

    const requestUrl = new URL(request.url);
    const backendUrl = new URL(buildBackendUrl(SAMPLES_ENDPOINT));
    requestUrl.searchParams.forEach((value, key) => {
      if (key !== "page" && key !== "page_size") {
        backendUrl.searchParams.set(key, value);
      }
    });

    backendUrl.searchParams.set("page", "1");
    backendUrl.searchParams.set("page_size", String(PAGE_SIZE));

    const rows: SampleRow[] = [];
    let nextUrl: string | null = backendUrl.toString();
    let pageCounter = 0;

    while (nextUrl && pageCounter < MAX_PAGES) {
      const response = await fetch(nextUrl, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        cache: "no-store",
      });

      if (!response.ok) {
        return NextResponse.json(
          { detail: `Failed to fetch samples (status ${response.status})` },
          { status: response.status },
        );
      }

      const payload = (await response.json()) as SampleApiPayload | SampleRow[];

      const items: SampleRow[] = Array.isArray(payload)
        ? payload
        : Array.isArray(payload?.results)
          ? payload.results ?? []
          : [];

      rows.push(...items);

      const nextLink =
        !Array.isArray(payload) && typeof payload?.next === "string" && payload.next.trim().length > 0
          ? payload.next
          : null;

      nextUrl = nextLink ? new URL(nextLink, backendUrl).toString() : null;
      pageCounter += 1;
    }

    const csvContents = buildCsv(rows);
    const now = new Date();
    const timestamp = `${now.getUTCFullYear()}${String(now.getUTCMonth() + 1).padStart(2, "0")}${String(
      now.getUTCDate(),
    ).padStart(2, "0")}_${String(now.getUTCHours()).padStart(2, "0")}${String(now.getUTCMinutes()).padStart(
      2,
      "0",
    )}${String(now.getUTCSeconds()).padStart(2, "0")}`;
    const filename = `samples-export-${timestamp}.csv`;

    return new NextResponse(csvContents, {
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": `attachment; filename="${filename}"`,
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    console.error("Failed to export samples CSV:", error);
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
