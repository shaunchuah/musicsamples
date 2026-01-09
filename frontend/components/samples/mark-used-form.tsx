// frontend/components/samples/mark-used-form.tsx
// Renders the QR scan mark-used form with scan handling and history.
// Exists to mirror the legacy mark-used workflow in the Next.js dashboard.

"use client";

import { ExternalLinkIcon } from "lucide-react";
import type { KeyboardEvent } from "react";
import { useEffect, useId, useMemo, useRef, useState } from "react";

import { AlertDescription, AlertError, AlertSuccess } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type ScanHistoryEntry = {
  sampleId: string;
  status: string;
  message: string;
};

export function MarkUsedForm() {
  const baseId = useId();
  const [sampleId, setSampleId] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [scanHistory, setScanHistory] = useState<ScanHistoryEntry[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const sampleIdRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (!successMessage && !errorMessage) {
      return;
    }

    const timer = window.setTimeout(() => {
      setSuccessMessage(null);
      setErrorMessage(null);
    }, 3000);

    return () => window.clearTimeout(timer);
  }, [successMessage, errorMessage]);

  useEffect(() => {
    if (!isSubmitting) {
      sampleIdRef.current?.focus();
    }
  }, [isSubmitting]);

  const recordHistory = (entry: ScanHistoryEntry) => {
    setScanHistory((prev) => [entry, ...prev]);
  };

  const handleSubmit = async () => {
    if (!sampleId.trim()) {
      setErrorMessage("Scan a sample ID to continue.");
      return;
    }

    setIsSubmitting(true);
    setFieldErrors({});

    try {
      const response = await fetch("/api/dashboard/qr-scan/mark-used", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ sample_id: sampleId }),
      });

      let payload: unknown = null;
      try {
        payload = await response.json();
      } catch {
        payload = null;
      }

      if (!response.ok) {
        let errorDetail = response.statusText || "Unable to mark sample as used.";
        const nextFieldErrors: Record<string, string> = {};
        const errorDetailsForHistory: string[] = [];

        if (payload && typeof payload === "object" && !Array.isArray(payload)) {
          const payloadRecord = payload as Record<string, unknown>;
          Object.entries(payloadRecord).forEach(([key, value]) => {
            if (key === "detail" || key === "error") {
              return;
            }
            if (Array.isArray(value)) {
              const fieldMessage = value.map(String).join(" ");
              nextFieldErrors[key] = fieldMessage;
              if (fieldMessage) {
                const entry = `${key}: ${fieldMessage}`;
                if (!errorDetailsForHistory.includes(entry)) {
                  errorDetailsForHistory.push(entry);
                }
              }
            } else if (typeof value === "string") {
              nextFieldErrors[key] = value;
              const entry = `${key}: ${value}`;
              if (!errorDetailsForHistory.includes(entry)) {
                errorDetailsForHistory.push(entry);
              }
            }
          });

          if (typeof payloadRecord.detail === "string") {
            errorDetail = payloadRecord.detail;
            if (!errorDetailsForHistory.includes(payloadRecord.detail)) {
              errorDetailsForHistory.push(payloadRecord.detail);
            }
          }

          if (typeof payloadRecord.error === "string") {
            errorDetail = payloadRecord.error;
            if (!errorDetailsForHistory.includes(payloadRecord.error)) {
              errorDetailsForHistory.push(payloadRecord.error);
            }
          }
        }

        setFieldErrors(nextFieldErrors);
        setErrorMessage(`${errorDetail} (Scanned ID: ${sampleId})`);
        recordHistory({
          sampleId,
          status: "Error",
          message: errorDetailsForHistory.length ? errorDetailsForHistory.join(" | ") : errorDetail,
        });
        return;
      }

      setSuccessMessage("Success - Sample Updated");
      recordHistory({
        sampleId,
        status: "Success",
        message: `Sample ${sampleId} marked as used.`,
      });
    } catch {
      setErrorMessage(`Something went wrong. (Scanned ID: ${sampleId})`);
      recordHistory({
        sampleId,
        status: "Error",
        message: "Something went wrong.",
      });
    } finally {
      setSampleId("");
      setIsSubmitting(false);
    }
  };

  const handleScanKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter" || event.key === "Tab") {
      event.preventDefault();
      handleSubmit();
    }
  };

  const formErrorSummary = useMemo(() => {
    return Object.entries(fieldErrors).map(([key, value]) => `${key}: ${value}`);
  }, [fieldErrors]);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Mark Samples as Used</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {formErrorSummary.length ? (
            <AlertError>
              <AlertDescription>
                <ul className="list-disc space-y-1 pl-5">
                  {formErrorSummary.map((message) => (
                    <li key={message}>{message}</li>
                  ))}
                </ul>
              </AlertDescription>
            </AlertError>
          ) : null}

          {successMessage ? (
            <AlertSuccess>
              <AlertDescription>{successMessage}</AlertDescription>
            </AlertSuccess>
          ) : null}
          {errorMessage ? (
            <AlertError>
              <AlertDescription>{errorMessage}</AlertDescription>
            </AlertError>
          ) : null}

          <Input
            id={`${baseId}-sample-id`}
            ref={sampleIdRef}
            value={sampleId}
            onChange={(event) => setSampleId(event.target.value)}
            onKeyDown={handleScanKeyDown}
            placeholder="Click here and start scanning barcodes or type sample IDs in..."
            aria-invalid={Boolean(fieldErrors.sample_id)}
            disabled={isSubmitting}
          />
          {fieldErrors.sample_id ? (
            <p className="text-sm text-destructive">{fieldErrors.sample_id}</p>
          ) : null}

          <Button type="button" onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? "Saving..." : "Submit scan"}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Scan History</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Sample ID</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Message</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {scanHistory.length ? (
                scanHistory.map((entry, index) => (
                  <TableRow key={`${entry.sampleId}-${index}`}>
                    <TableCell>{entry.sampleId}</TableCell>
                    <TableCell>{entry.status}</TableCell>
                    <TableCell>
                      <span>{entry.message}</span>
                      {entry.status === "Success" ? (
                        <>
                          {" "}
                          <a
                            href={`/samples/${encodeURIComponent(entry.sampleId)}`}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 text-primary underline-offset-4 hover:underline"
                          >
                            (View sample <ExternalLinkIcon className="size-3" />)
                          </a>
                        </>
                      ) : null}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={3} className="text-muted-foreground">
                    No scans yet.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
