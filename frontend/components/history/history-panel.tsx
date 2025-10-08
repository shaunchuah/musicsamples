// frontend/components/history/history-panel.tsx
// Renders an audit history card with metadata and change timeline entries.
// Centralises the audit presentation shared by samples, boxes, and experiments.

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

type HistoryChange = {
  field: string;
  label: string;
  old: string | null;
  new: string | null;
};

type HistoryEntry = {
  timestamp: string;
  user: string | null;
  summary?: string | null;
  changes: HistoryChange[];
};

type HistorySummary = {
  created: string;
  createdBy: string | null;
  lastModified: string;
  lastModifiedBy: string | null;
};

type HistoryPanelProps = {
  title?: string;
  description?: string;
  summary: HistorySummary;
  entries: HistoryEntry[];
};

const timestampFormatter = new Intl.DateTimeFormat("en-GB", {
  year: "numeric",
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return timestampFormatter.format(date);
}

function formatValue(value: string | null): string {
  if (value === null || value === "") {
    return "—";
  }
  return value;
}

export function HistoryPanel({
  title = "History",
  description = "Recent changes and audit events.",
  summary,
  entries,
}: HistoryPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[320px] table-fixed border-collapse text-left text-sm">
            <tbody>
              <tr className="border-b border-border/40">
                <th className="w-1/2 px-2 py-2 font-semibold text-muted-foreground">First Registered</th>
                <td className="px-2 py-2">{formatTimestamp(summary.created)}</td>
              </tr>
              <tr className="border-b border-border/40">
                <th className="w-1/2 px-2 py-2 font-semibold text-muted-foreground">Created By</th>
                <td className="px-2 py-2">{formatValue(summary.createdBy)}</td>
              </tr>
              <tr className="border-b border-border/40">
                <th className="w-1/2 px-2 py-2 font-semibold text-muted-foreground">Last Modified</th>
                <td className="px-2 py-2">{formatTimestamp(summary.lastModified)}</td>
              </tr>
              <tr>
                <th className="w-1/2 px-2 py-2 font-semibold text-muted-foreground">Modified By</th>
                <td className="px-2 py-2">{formatValue(summary.lastModifiedBy)}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="space-y-4">
          {entries.map((entry, index) => (
            <div key={`${entry.timestamp}-${index}`} className="rounded-md border border-border/40 p-3">
              <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-muted-foreground">
                <span>{formatTimestamp(entry.timestamp)}</span>
                <span>{formatValue(entry.user)}</span>
              </div>
              {entry.summary ? <p className="mt-2 text-sm">{entry.summary}</p> : null}
              {entry.changes.length > 0 ? (
                <dl className="mt-3 space-y-2 text-sm">
                  {entry.changes.map((change, changeIndex) => (
                    <div key={`${change.field}-${changeIndex}`} className="border-t border-border/30 pt-2 first:border-0 first:pt-0">
                      <dt className="font-medium text-foreground">{change.label}</dt>
                      <dd className="text-muted-foreground">
                        {formatValue(change.old)} → {formatValue(change.new)}
                      </dd>
                    </div>
                  ))}
                </dl>
              ) : null}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
