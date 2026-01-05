// frontend/components/samples/update-location-form.tsx
// Renders the QR scan update-location form with scan handling and history.
// Exists to mirror the legacy update-location workflow in the Next.js dashboard.

"use client";

import type { KeyboardEvent } from "react";
import { useEffect, useId, useMemo, useRef, useState } from "react";

import { AlertDescription, AlertError, AlertSuccess } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type FormState = {
  sample_location: string;
  sample_sublocation: string;
  sample_id: string;
};

type ScanHistoryEntry = {
  sampleId: string;
  status: string;
  sampleLocation: string;
  sampleSublocation: string;
  message: string;
};

const INITIAL_FORM_STATE: FormState = {
  sample_location: "",
  sample_sublocation: "",
  sample_id: "",
};

function useAutocomplete(endpoint: string) {
  const [options, setOptions] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const requestOptions = async (term: string) => {
    const trimmed = term.trim();
    if (!trimmed) {
      setOptions([]);
      return;
    }

    try {
      setError(null);
      const response = await fetch(`${endpoint}?term=${encodeURIComponent(trimmed)}`, {
        cache: "no-store",
      });
      if (!response.ok) {
        setError("Unable to load suggestions.");
        return;
      }

      const data = (await response.json()) as unknown;
      if (Array.isArray(data)) {
        setOptions(data.filter((value) => typeof value === "string"));
      } else {
        setOptions([]);
      }
    } catch {
      setError("Unable to load suggestions.");
    }
  };

  return { options, requestOptions, error };
}

export function UpdateLocationForm() {
  const baseId = useId();
  const [formState, setFormState] = useState<FormState>(INITIAL_FORM_STATE);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [scanHistory, setScanHistory] = useState<ScanHistoryEntry[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const sampleIdRef = useRef<HTMLInputElement | null>(null);

  const locationAutocomplete = useAutocomplete("/api/dashboard/qr-scan/autocomplete/locations");
  const sublocationAutocomplete = useAutocomplete(
    "/api/dashboard/qr-scan/autocomplete/sublocations",
  );

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

  const handleFieldChange = <Key extends keyof FormState>(key: Key, value: FormState[Key]) => {
    setFormState((prev) => ({ ...prev, [key]: value }));
    setFieldErrors((prev) => {
      if (!prev[key]) {
        return prev;
      }
      const next = { ...prev };
      delete next[key];
      return next;
    });
  };

  const recordHistory = (entry: ScanHistoryEntry) => {
    setScanHistory((prev) => [entry, ...prev]);
  };

  const handleSubmit = async () => {
    if (!formState.sample_id.trim()) {
      setErrorMessage("Scan a sample ID to continue.");
      return;
    }

    setIsSubmitting(true);
    setFieldErrors({});

    try {
      const response = await fetch("/api/dashboard/qr-scan/update-location", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sample_id: formState.sample_id,
          sample_location: formState.sample_location,
          sample_sublocation: formState.sample_sublocation,
        }),
      });

      let payload: unknown = null;
      try {
        payload = await response.json();
      } catch {
        payload = null;
      }

      if (!response.ok) {
        let errorDetail = response.statusText || "Unable to update sample.";
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
        setErrorMessage(`${errorDetail} (Scanned ID: ${formState.sample_id})`);
        recordHistory({
          sampleId: formState.sample_id,
          status: "Error",
          sampleLocation: "",
          sampleSublocation: "",
          message: errorDetailsForHistory.length ? errorDetailsForHistory.join(" | ") : errorDetail,
        });
        return;
      }

      setSuccessMessage("Success - Sample Updated");
      recordHistory({
        sampleId: formState.sample_id,
        status: "Success",
        sampleLocation: formState.sample_location,
        sampleSublocation: formState.sample_sublocation,
        message: `Sample ${formState.sample_id} updated.`,
      });
    } catch {
      setErrorMessage(`Something went wrong. (Scanned ID: ${formState.sample_id})`);
      recordHistory({
        sampleId: formState.sample_id,
        status: "Error - Something went wrong",
        sampleLocation: "Error",
        sampleSublocation: "Error",
        message: "Something went wrong.",
      });
    } finally {
      setFormState((prev) => ({ ...prev, sample_id: "" }));
      setIsSubmitting(false);
      sampleIdRef.current?.focus();
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
          <CardTitle>Instructions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm text-muted-foreground">
          <div>
            <p className="font-semibold text-foreground">Steps:</p>
            <ol className="list-decimal space-y-1 pl-5">
              <li>Set the appropriate location and sublocation.</li>
              <li>Click the barcode ID scanning area and start scanning QR codes.</li>
            </ol>
          </div>
          <p>
            <span className="font-semibold text-foreground">Tip:</span> If a label won't scan, you
            can type in the sample ID and hit enter instead.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Sample Location</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
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

          <div className="space-y-2">
            <Label htmlFor={`${baseId}-sample-location`}>Sample Location</Label>
            <Input
              id={`${baseId}-sample-location`}
              list={`${baseId}-sample-location-options`}
              value={formState.sample_location}
              onChange={(event) => {
                handleFieldChange("sample_location", event.target.value);
                locationAutocomplete.requestOptions(event.target.value);
              }}
              autoComplete="off"
              aria-invalid={Boolean(fieldErrors.sample_location)}
            />
            {fieldErrors.sample_location ? (
              <p className="text-sm text-destructive">{fieldErrors.sample_location}</p>
            ) : null}
            {locationAutocomplete.error ? (
              <p className="text-xs text-muted-foreground">{locationAutocomplete.error}</p>
            ) : null}
            <datalist id={`${baseId}-sample-location-options`}>
              {locationAutocomplete.options.map((option) => (
                <option key={option} value={option} />
              ))}
            </datalist>
          </div>

          <div className="space-y-2">
            <Label htmlFor={`${baseId}-sample-sublocation`}>Sample Sublocation</Label>
            <Input
              id={`${baseId}-sample-sublocation`}
              list={`${baseId}-sample-sublocation-options`}
              value={formState.sample_sublocation}
              onChange={(event) => {
                handleFieldChange("sample_sublocation", event.target.value);
                sublocationAutocomplete.requestOptions(event.target.value);
              }}
              autoComplete="off"
              aria-invalid={Boolean(fieldErrors.sample_sublocation)}
            />
            {fieldErrors.sample_sublocation ? (
              <p className="text-sm text-destructive">{fieldErrors.sample_sublocation}</p>
            ) : null}
            {sublocationAutocomplete.error ? (
              <p className="text-xs text-muted-foreground">{sublocationAutocomplete.error}</p>
            ) : null}
            <datalist id={`${baseId}-sample-sublocation-options`}>
              {sublocationAutocomplete.options.map((option) => (
                <option key={option} value={option} />
              ))}
            </datalist>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Barcode ID scanning area</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
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
            value={formState.sample_id}
            onChange={(event) => handleFieldChange("sample_id", event.target.value)}
            onKeyDown={handleScanKeyDown}
            placeholder="Click here and start scanning barcodes..."
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
                <TableHead>Sample Location</TableHead>
                <TableHead>Sample Sublocation</TableHead>
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
                            (View sample)
                          </a>
                        </>
                      ) : null}
                    </TableCell>
                    <TableCell>{entry.sampleLocation}</TableCell>
                    <TableCell>{entry.sampleSublocation}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} className="text-muted-foreground">
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
