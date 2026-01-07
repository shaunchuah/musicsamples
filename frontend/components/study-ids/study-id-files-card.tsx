// frontend/components/study-ids/study-id-files-card.tsx
// Shows the list of files that point to the current study identifier.
// Exists so the detail page can surface linked files without duplicating the datastore fetch logic.

"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

type FileSummary = {
  id: number;
  file_name: string | null;
};

type StudyIdFilesCardProps = {
  studyId: number;
};

export function StudyIdFilesCard({ studyId }: StudyIdFilesCardProps) {
  const [files, setFiles] = useState<FileSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    async function loadFiles() {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/dashboard/study-ids/${studyId}/files`, {
          signal: controller.signal,
          cache: "no-store",
        });
        if (!response.ok) {
          throw new Error("Unable to load files.");
        }
        const payload = (await response.json().catch(() => null)) as FileSummary[] | null;
        setFiles(Array.isArray(payload) ? payload : []);
      } catch (err) {
        if (controller.signal.aborted) {
          return;
        }
        setError(err instanceof Error ? err.message : "Unable to load files.");
        setFiles([]);
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    loadFiles();
    return () => controller.abort();
  }, [studyId]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Linked files</CardTitle>
        <CardDescription>Files stored under this study ID.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        {isLoading ? (
          <p className="text-muted-foreground">Loading files…</p>
        ) : error ? (
          <p className="text-destructive">{error}</p>
        ) : files.length === 0 ? (
          <p className="text-muted-foreground">No files uploaded yet.</p>
        ) : (
          <ul className="space-y-1">
            {files.map((file) => (
              <li key={file.id}>
                <Link
                  href={`/datastore/read/${file.id}`}
                  className="font-medium text-primary underline-offset-2 hover:underline"
                >
                  {file.file_name ?? "File"}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
