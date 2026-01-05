// frontend/components/samples/add-multiple-form.tsx
// Renders the QR scan add-multiple form, including scan handling, errors, and history.
// Exists to replicate the legacy barcode add-multiple workflow inside the Next.js dashboard.

"use client";

import { ExternalLinkIcon } from "lucide-react";
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
import { Textarea } from "@/components/ui/textarea";

const STUDY_OPTIONS = [
  { value: "", label: "---------" },
  { value: "gidamps", label: "GI-DAMPs" },
  { value: "music", label: "MUSIC" },
  { value: "mini_music", label: "Mini-MUSIC" },
  { value: "marvel", label: "MARVEL" },
  { value: "fate_cd", label: "FATE-CD" },
  { value: "none", label: "None" },
];

const MUSIC_TIMEPOINT_OPTIONS = [
  { value: "", label: "---------" },
  { value: "baseline", label: "Baseline" },
  { value: "3_months", label: "3 Months" },
  { value: "6_months", label: "6 Months" },
  { value: "9_months", label: "9 Months" },
  { value: "12_months", label: "12 Months" },
];

const MARVEL_TIMEPOINT_OPTIONS = [
  { value: "", label: "---------" },
  { value: "baseline", label: "Baseline" },
  { value: "12_weeks", label: "12 Weeks" },
  { value: "24_weeks", label: "24 Weeks" },
];

const SAMPLE_TYPE_OPTIONS = [
  { value: "", label: "---------" },
  { value: "standard_edta", label: "Standard EDTA tube" },
  { value: "edta_plasma", label: "EDTA plasma child aliquot" },
  { value: "cfdna_tube", label: "PaxGene cfDNA tube" },
  { value: "cfdna_plasma", label: "PaxGene cfDNA plasma" },
  { value: "cfdna_extracted", label: "Extracted cfDNA" },
  { value: "paxgene_rna", label: "PaxGene RNA tube" },
  { value: "rna_plasma", label: "PaxGene RNA child aliquot" },
  { value: "standard_gel", label: "Standard gel tube" },
  { value: "serum", label: "Serum" },
  { value: "biopsy_formalin", label: "Formalin biopsy" },
  { value: "biopsy_rnalater", label: "RNAlater biopsy" },
  { value: "paraffin_block", label: "Paraffin block" },
  { value: "stool_standard", label: "Standard stool" },
  { value: "stool_calprotectin", label: "Calprotectin" },
  { value: "stool_qfit", label: "qFIT" },
  { value: "stool_omnigut", label: "OmniGut" },
  { value: "stool_supernatant", label: "Stool supernatant" },
  { value: "saliva", label: "Saliva" },
  { value: "other", label: "Other - please specify in comments" },
];

const HAEMOLYSIS_OPTIONS = [
  { value: "", label: "Select category" },
  { value: "0", label: "Minimal" },
  { value: "20", label: "20 mg/dL" },
  { value: "50", label: "50 mg/dL" },
  { value: "100", label: "100 mg/dL (unusable)" },
  { value: "250", label: "250 mg/dL (unusable)" },
  { value: "500", label: "500 mg/dL (unusable)" },
  { value: "1000", label: "1000 mg/dL (unusable)" },
];

const BIOPSY_LOCATION_OPTIONS = [
  { value: "", label: "---------" },
  { value: "terminal_ileum", label: "Terminal ileum" },
  { value: "caecum", label: "Caecum" },
  { value: "ascending", label: "Ascending colon" },
  { value: "transverse", label: "Transverse colon" },
  { value: "descending", label: "Descending colon" },
  { value: "sigmoid", label: "Sigmoid colon" },
  { value: "rectum", label: "Rectum" },
  { value: "right_colon", label: "Right colon" },
  { value: "left_colon", label: "Left colon" },
  { value: "oesophagus", label: "Oesophagus" },
  { value: "stomach", label: "Stomach" },
  { value: "duodenum", label: "Duodenum" },
];

const BIOPSY_STATUS_OPTIONS = [
  { value: "", label: "Select inflamed status" },
  { value: "inflamed", label: "Inflamed" },
  { value: "uninflamed", label: "Uninflamed" },
  { value: "healthy", label: "Healthy" },
];

const VOLUME_UNIT_OPTIONS = [
  { value: "", label: "Select unit" },
  { value: "ml", label: "ml" },
  { value: "ul", label: "ul" },
];

type FormState = {
  sample_location: string;
  sample_sublocation: string;
  study_name: string;
  music_timepoint: string;
  marvel_timepoint: string;
  study_id: string;
  sample_type: string;
  qubit_cfdna_ng_ul: string;
  haemolysis_reference: string;
  paraffin_block_key: string;
  biopsy_location: string;
  biopsy_inflamed_status: string;
  sample_datetime: string;
  processing_datetime: string;
  frozen_datetime: string;
  sample_comments: string;
  sample_volume: string;
  sample_volume_units: string;
  freeze_thaw_count: string;
  sample_id: string;
};

type ScanHistoryEntry = {
  sampleId: string;
  status: "Success" | "Error";
  message: string;
};

const FIELD_LABELS: Record<keyof FormState, string> = {
  sample_location: "Sample Location",
  sample_sublocation: "Sample Sublocation",
  study_name: "Study Name",
  music_timepoint: "Music Timepoint",
  marvel_timepoint: "Marvel Timepoint",
  study_id: "Study ID",
  sample_type: "Sample Type",
  qubit_cfdna_ng_ul: "Qubit",
  haemolysis_reference: "Haemolysis Reference",
  paraffin_block_key: "Paraffin Block Key",
  biopsy_location: "Biopsy Location",
  biopsy_inflamed_status: "Biopsy Inflamed Status",
  sample_datetime: "Sampling Datetime",
  processing_datetime: "Processing Datetime",
  frozen_datetime: "Frozen Datetime",
  sample_comments: "Comments",
  sample_volume: "Volume Remaining",
  sample_volume_units: "Sample Volume Units",
  freeze_thaw_count: "Freeze-Thaw Count",
  sample_id: "Sample ID",
};

const INITIAL_FORM_STATE: FormState = {
  sample_location: "",
  sample_sublocation: "",
  study_name: "",
  music_timepoint: "",
  marvel_timepoint: "",
  study_id: "",
  sample_type: "",
  qubit_cfdna_ng_ul: "",
  haemolysis_reference: "",
  paraffin_block_key: "",
  biopsy_location: "",
  biopsy_inflamed_status: "",
  sample_datetime: "",
  processing_datetime: "",
  frozen_datetime: "",
  sample_comments: "",
  sample_volume: "",
  sample_volume_units: "",
  freeze_thaw_count: "0",
  sample_id: "",
};

function emptyToNull(value: string): string | null {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

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

export function AddMultipleForm() {
  const baseId = useId();
  const [formState, setFormState] = useState<FormState>(INITIAL_FORM_STATE);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [nonFieldError, setNonFieldError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [scanHistory, setScanHistory] = useState<ScanHistoryEntry[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const sampleIdRef = useRef<HTMLInputElement | null>(null);

  const locationAutocomplete = useAutocomplete("/api/dashboard/qr-scan/autocomplete/locations");
  const sublocationAutocomplete = useAutocomplete(
    "/api/dashboard/qr-scan/autocomplete/sublocations",
  );
  const studyIdAutocomplete = useAutocomplete("/api/dashboard/qr-scan/autocomplete/study-ids");

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

  const showMusicTimepoint =
    formState.study_name === "music" || formState.study_name === "mini_music";
  const showMarvelTimepoint = formState.study_name === "marvel";
  const showBiopsyFields = ["biopsy_formalin", "biopsy_rnalater", "paraffin_block"].includes(
    formState.sample_type,
  );
  const showParaffinBlock = formState.sample_type === "paraffin_block";
  const showHaemolysis = ["edta_plasma", "cfdna_plasma", "cfdna_extracted"].includes(
    formState.sample_type,
  );
  const showQubit = formState.sample_type === "cfdna_extracted";

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

  const clearValidation = () => {
    setFieldErrors({});
    setNonFieldError(null);
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
    clearValidation();

    try {
      const response = await fetch("/api/dashboard/qr-scan/add-multiple", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          study_name: formState.study_name,
          music_timepoint: formState.music_timepoint,
          marvel_timepoint: formState.marvel_timepoint,
          sample_id: formState.sample_id,
          sample_location: formState.sample_location,
          sample_sublocation: formState.sample_sublocation,
          study_id: formState.study_id,
          sample_type: formState.sample_type,
          qubit_cfdna_ng_ul: formState.qubit_cfdna_ng_ul,
          haemolysis_reference: formState.haemolysis_reference,
          paraffin_block_key: formState.paraffin_block_key,
          biopsy_location: formState.biopsy_location,
          biopsy_inflamed_status: formState.biopsy_inflamed_status,
          sample_datetime: emptyToNull(formState.sample_datetime),
          processing_datetime: emptyToNull(formState.processing_datetime),
          frozen_datetime: emptyToNull(formState.frozen_datetime),
          sample_comments: formState.sample_comments,
          sample_volume: formState.sample_volume,
          sample_volume_units: formState.sample_volume_units,
          freeze_thaw_count: formState.freeze_thaw_count,
        }),
      });

      let payload: unknown = null;
      try {
        payload = await response.json();
      } catch {
        payload = null;
      }

      if (!response.ok) {
        const nextFieldErrors: Record<string, string> = {};
        let errorDetail = response.statusText || "Unable to save sample.";
        const errorDetailsForHistory: string[] = [];

        if (payload && typeof payload === "object" && !Array.isArray(payload)) {
          const payloadRecord = payload as Record<string, unknown>;
          const nonField = payloadRecord.non_field_errors;
          if (Array.isArray(nonField)) {
            const nonFieldMessage = nonField.join(" ");
            setNonFieldError(nonFieldMessage);
            if (nonFieldMessage) {
              errorDetailsForHistory.push(nonFieldMessage);
            }
          }

          Object.entries(payloadRecord).forEach(([key, value]) => {
            if (key === "non_field_errors") {
              return;
            }
            if (Array.isArray(value)) {
              const fieldMessage = value.map(String).join(" ");
              nextFieldErrors[key] = fieldMessage;
              if (fieldMessage) {
                errorDetailsForHistory.push(
                  `${FIELD_LABELS[key as keyof FormState] ?? key}: ${fieldMessage}`,
                );
              }
            } else if (typeof value === "string") {
              nextFieldErrors[key] = value;
              errorDetailsForHistory.push(
                `${FIELD_LABELS[key as keyof FormState] ?? key}: ${value}`,
              );
            }
          });

          if (typeof payloadRecord.detail === "string") {
            errorDetail = payloadRecord.detail;
            errorDetailsForHistory.push(payloadRecord.detail);
          }

          if (typeof payloadRecord.error === "string") {
            errorDetail = payloadRecord.error;
            errorDetailsForHistory.push(payloadRecord.error);
          }
        }

        setFieldErrors(nextFieldErrors);
        setErrorMessage(`${errorDetail} (Scanned ID: ${formState.sample_id})`);
        recordHistory({
          sampleId: formState.sample_id,
          status: "Error",
          message: errorDetailsForHistory.length ? errorDetailsForHistory.join(" | ") : errorDetail,
        });
        return;
      }

      setSuccessMessage("Success - Sample Updated");
      recordHistory({
        sampleId: formState.sample_id,
        status: "Success",
        message: `Sample ${formState.sample_id} captured.`,
      });
    } catch {
      setErrorMessage(`Something went wrong. (Scanned ID: ${formState.sample_id})`);
      recordHistory({
        sampleId: formState.sample_id,
        status: "Error",
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
    const errors = Object.entries(fieldErrors).map(([key, value]) => {
      const label = FIELD_LABELS[key as keyof FormState] || key;
      return `${label}: ${value}`;
    });

    if (nonFieldError) {
      errors.unshift(nonFieldError);
    }

    return errors;
  }, [fieldErrors, nonFieldError]);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Instructions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm text-muted-foreground">
          <p>
            <span className="font-semibold text-foreground">Important Note:</span> Barcode scanners
            work like keyboards. For most scanners, the default is to provide the enter key after
            scanning a barcode. Some scanners may need to be configured to provide the enter or tab
            key on scan. This page accepts both enter and tab keys from barcode scanners.
          </p>
          <div>
            <p className="font-semibold text-foreground">Steps:</p>
            <ol className="list-decimal space-y-1 pl-5">
              <li>Fill in the required details</li>
              <li>Start scanning to tag samples with those details</li>
            </ol>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Sample Details</CardTitle>
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

          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor={`${baseId}-sample-location`}>Sample Location*</Label>
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
          </div>

          <div className="space-y-2">
            <Label htmlFor={`${baseId}-study-name`}>Study Name*</Label>
            <select
              id={`${baseId}-study-name`}
              value={formState.study_name}
              onChange={(event) => handleFieldChange("study_name", event.target.value)}
              className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
              aria-invalid={Boolean(fieldErrors.study_name)}
            >
              {STUDY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {fieldErrors.study_name ? (
              <p className="text-sm text-destructive">{fieldErrors.study_name}</p>
            ) : null}
          </div>

          {showMusicTimepoint ? (
            <div className="space-y-2">
              <Label htmlFor={`${baseId}-music-timepoint`}>Music Timepoint</Label>
              <select
                id={`${baseId}-music-timepoint`}
                value={formState.music_timepoint}
                onChange={(event) => handleFieldChange("music_timepoint", event.target.value)}
                className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
                aria-invalid={Boolean(fieldErrors.music_timepoint)}
              >
                {MUSIC_TIMEPOINT_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {fieldErrors.music_timepoint ? (
                <p className="text-sm text-destructive">{fieldErrors.music_timepoint}</p>
              ) : null}
            </div>
          ) : null}

          {showMarvelTimepoint ? (
            <div className="space-y-2">
              <Label htmlFor={`${baseId}-marvel-timepoint`}>Marvel Timepoint</Label>
              <select
                id={`${baseId}-marvel-timepoint`}
                value={formState.marvel_timepoint}
                onChange={(event) => handleFieldChange("marvel_timepoint", event.target.value)}
                className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
                aria-invalid={Boolean(fieldErrors.marvel_timepoint)}
              >
                {MARVEL_TIMEPOINT_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {fieldErrors.marvel_timepoint ? (
                <p className="text-sm text-destructive">{fieldErrors.marvel_timepoint}</p>
              ) : null}
            </div>
          ) : null}

          <div className="space-y-2">
            <Label htmlFor={`${baseId}-study-id`}>Study ID*</Label>
            <Input
              id={`${baseId}-study-id`}
              list={`${baseId}-study-id-options`}
              value={formState.study_id}
              onChange={(event) => {
                handleFieldChange("study_id", event.target.value);
                studyIdAutocomplete.requestOptions(event.target.value);
              }}
              autoComplete="off"
              aria-invalid={Boolean(fieldErrors.study_id)}
            />
            {fieldErrors.study_id ? (
              <p className="text-sm text-destructive">{fieldErrors.study_id}</p>
            ) : null}
            {studyIdAutocomplete.error ? (
              <p className="text-xs text-muted-foreground">{studyIdAutocomplete.error}</p>
            ) : null}
            <datalist id={`${baseId}-study-id-options`}>
              {studyIdAutocomplete.options.map((option) => (
                <option key={option} value={option} />
              ))}
            </datalist>
          </div>

          <div className="space-y-2">
            <Label htmlFor={`${baseId}-sample-type`}>Sample Type*</Label>
            <select
              id={`${baseId}-sample-type`}
              value={formState.sample_type}
              onChange={(event) => handleFieldChange("sample_type", event.target.value)}
              className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
              aria-invalid={Boolean(fieldErrors.sample_type)}
            >
              {SAMPLE_TYPE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {fieldErrors.sample_type ? (
              <p className="text-sm text-destructive">{fieldErrors.sample_type}</p>
            ) : null}
          </div>

          {showQubit ? (
            <div className="space-y-2">
              <Label htmlFor={`${baseId}-qubit`}>Qubit (ng/uL)</Label>
              <Input
                id={`${baseId}-qubit`}
                type="number"
                step="0.001"
                value={formState.qubit_cfdna_ng_ul}
                onChange={(event) => handleFieldChange("qubit_cfdna_ng_ul", event.target.value)}
                aria-invalid={Boolean(fieldErrors.qubit_cfdna_ng_ul)}
              />
              {fieldErrors.qubit_cfdna_ng_ul ? (
                <p className="text-sm text-destructive">{fieldErrors.qubit_cfdna_ng_ul}</p>
              ) : null}
            </div>
          ) : null}

          {showHaemolysis ? (
            <div className="space-y-2">
              <Label htmlFor={`${baseId}-haemolysis`}>Haemolysis Reference Palette</Label>
              <select
                id={`${baseId}-haemolysis`}
                value={formState.haemolysis_reference}
                onChange={(event) => handleFieldChange("haemolysis_reference", event.target.value)}
                className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
                aria-invalid={Boolean(fieldErrors.haemolysis_reference)}
              >
                {HAEMOLYSIS_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {fieldErrors.haemolysis_reference ? (
                <p className="text-sm text-destructive">{fieldErrors.haemolysis_reference}</p>
              ) : null}
            </div>
          ) : null}

          {showParaffinBlock ? (
            <div className="space-y-2">
              <Label htmlFor={`${baseId}-paraffin-block-key`}>Paraffin Block Key</Label>
              <Input
                id={`${baseId}-paraffin-block-key`}
                value={formState.paraffin_block_key}
                onChange={(event) => handleFieldChange("paraffin_block_key", event.target.value)}
                aria-invalid={Boolean(fieldErrors.paraffin_block_key)}
              />
              {fieldErrors.paraffin_block_key ? (
                <p className="text-sm text-destructive">{fieldErrors.paraffin_block_key}</p>
              ) : null}
            </div>
          ) : null}

          {showBiopsyFields ? (
            <div className="grid gap-6 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor={`${baseId}-biopsy-location`}>Biopsy Location</Label>
                <select
                  id={`${baseId}-biopsy-location`}
                  value={formState.biopsy_location}
                  onChange={(event) => handleFieldChange("biopsy_location", event.target.value)}
                  className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  aria-invalid={Boolean(fieldErrors.biopsy_location)}
                >
                  {BIOPSY_LOCATION_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                {fieldErrors.biopsy_location ? (
                  <p className="text-sm text-destructive">{fieldErrors.biopsy_location}</p>
                ) : null}
              </div>
              <div className="space-y-2">
                <Label htmlFor={`${baseId}-biopsy-status`}>Biopsy Inflamed Status</Label>
                <select
                  id={`${baseId}-biopsy-status`}
                  value={formState.biopsy_inflamed_status}
                  onChange={(event) =>
                    handleFieldChange("biopsy_inflamed_status", event.target.value)
                  }
                  className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  aria-invalid={Boolean(fieldErrors.biopsy_inflamed_status)}
                >
                  {BIOPSY_STATUS_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                {fieldErrors.biopsy_inflamed_status ? (
                  <p className="text-sm text-destructive">{fieldErrors.biopsy_inflamed_status}</p>
                ) : null}
              </div>
            </div>
          ) : null}

          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor={`${baseId}-sample-datetime`}>Sampling Datetime*</Label>
              <Input
                id={`${baseId}-sample-datetime`}
                type="datetime-local"
                value={formState.sample_datetime}
                onChange={(event) => handleFieldChange("sample_datetime", event.target.value)}
                aria-invalid={Boolean(fieldErrors.sample_datetime)}
              />
              {fieldErrors.sample_datetime ? (
                <p className="text-sm text-destructive">{fieldErrors.sample_datetime}</p>
              ) : null}
            </div>
            <div className="space-y-2">
              <Label htmlFor={`${baseId}-processing-datetime`}>Processing Datetime</Label>
              <Input
                id={`${baseId}-processing-datetime`}
                type="datetime-local"
                value={formState.processing_datetime}
                onChange={(event) => handleFieldChange("processing_datetime", event.target.value)}
                aria-invalid={Boolean(fieldErrors.processing_datetime)}
              />
              {fieldErrors.processing_datetime ? (
                <p className="text-sm text-destructive">{fieldErrors.processing_datetime}</p>
              ) : null}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor={`${baseId}-frozen-datetime`}>Frozen Datetime (if applicable)</Label>
            <Input
              id={`${baseId}-frozen-datetime`}
              type="datetime-local"
              value={formState.frozen_datetime}
              onChange={(event) => handleFieldChange("frozen_datetime", event.target.value)}
              aria-invalid={Boolean(fieldErrors.frozen_datetime)}
            />
            {fieldErrors.frozen_datetime ? (
              <p className="text-sm text-destructive">{fieldErrors.frozen_datetime}</p>
            ) : null}
          </div>

          <div className="space-y-2">
            <Label htmlFor={`${baseId}-sample-comments`}>Comments</Label>
            <Textarea
              id={`${baseId}-sample-comments`}
              rows={4}
              value={formState.sample_comments}
              onChange={(event) => handleFieldChange("sample_comments", event.target.value)}
              aria-invalid={Boolean(fieldErrors.sample_comments)}
            />
            {fieldErrors.sample_comments ? (
              <p className="text-sm text-destructive">{fieldErrors.sample_comments}</p>
            ) : null}
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor={`${baseId}-sample-volume`}>Volume Remaining (est.)</Label>
              <Input
                id={`${baseId}-sample-volume`}
                type="number"
                step="0.001"
                value={formState.sample_volume}
                onChange={(event) => handleFieldChange("sample_volume", event.target.value)}
                aria-invalid={Boolean(fieldErrors.sample_volume)}
              />
              {fieldErrors.sample_volume ? (
                <p className="text-sm text-destructive">{fieldErrors.sample_volume}</p>
              ) : null}
            </div>
            <div className="space-y-2">
              <Label htmlFor={`${baseId}-sample-volume-units`}>Sample Volume Units</Label>
              <select
                id={`${baseId}-sample-volume-units`}
                value={formState.sample_volume_units}
                onChange={(event) => handleFieldChange("sample_volume_units", event.target.value)}
                className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
                aria-invalid={Boolean(fieldErrors.sample_volume_units)}
              >
                {VOLUME_UNIT_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {fieldErrors.sample_volume_units ? (
                <p className="text-sm text-destructive">{fieldErrors.sample_volume_units}</p>
              ) : null}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor={`${baseId}-freeze-thaw-count`}>No. of Freeze-Thaw Cycles</Label>
            <Input
              id={`${baseId}-freeze-thaw-count`}
              type="number"
              value={formState.freeze_thaw_count}
              onChange={(event) => handleFieldChange("freeze_thaw_count", event.target.value)}
              aria-invalid={Boolean(fieldErrors.freeze_thaw_count)}
            />
            {fieldErrors.freeze_thaw_count ? (
              <p className="text-sm text-destructive">{fieldErrors.freeze_thaw_count}</p>
            ) : null}
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
                          (
                          <a
                            href={`/samples/${encodeURIComponent(entry.sampleId)}`}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 text-primary underline-offset-4 hover:underline"
                          >
                            View sample <ExternalLinkIcon className="size-3" />
                          </a>
                          )
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
