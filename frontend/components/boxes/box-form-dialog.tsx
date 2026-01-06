// frontend/components/boxes/box-form-dialog.tsx
// Renders the modal form used to create a new basic science box from the dashboard.
// Exists to keep the boxes table focused while providing a dedicated creation workflow.

"use client";

import type { ChangeEvent, FormEvent } from "react";
import { useEffect, useId, useMemo, useState } from "react";

import { AlertDescription, AlertError } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  MultiSelect,
  MultiSelectContent,
  MultiSelectItem,
  MultiSelectTrigger,
  MultiSelectValue,
} from "@/components/ui/multi-select";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

type BoxOption = {
  value: string;
  label: string;
};

type ExperimentOption = {
  id: number;
  label: string;
};

type BoxOptionsResponse = {
  box_type_options: BoxOption[];
  location_options: BoxOption[];
  row_options: BoxOption[];
  column_options: BoxOption[];
  depth_options: BoxOption[];
  experiments: ExperimentOption[];
};

type BoxFormValues = {
  box_id: string;
  box_type: string;
  location: string;
  row: string;
  column: string;
  depth: string;
  comments: string;
  experiments: string[];
};

type BoxFormDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: () => void;
};

const EMPTY_FORM: BoxFormValues = {
  box_id: "",
  box_type: "",
  location: "",
  row: "",
  column: "",
  depth: "",
  comments: "",
  experiments: [],
};

const EMPTY_SELECT_VALUE = "__none__";

function normaliseNullable(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function formatErrorMessage(payload: unknown) {
  if (!payload || typeof payload !== "object") {
    return "Unable to create the box. Please try again.";
  }
  const data = payload as Record<string, unknown>;
  if (typeof data.detail === "string") {
    return data.detail;
  }
  const entries = Object.entries(data).flatMap(([key, value]) => {
    if (Array.isArray(value)) {
      return `${key}: ${value.join(" ")}`;
    }
    if (typeof value === "string") {
      return `${key}: ${value}`;
    }
    return `${key}: Invalid value.`;
  });
  return entries.length ? entries.join(" ") : "Unable to create the box. Please try again.";
}

export function BoxFormDialog({ open, onOpenChange, onCreated }: BoxFormDialogProps) {
  const idPrefix = useId();
  const fieldIds = useMemo(
    () => ({
      boxId: `${idPrefix}-box-id`,
      boxType: `${idPrefix}-box-type`,
      location: `${idPrefix}-box-location`,
      row: `${idPrefix}-box-row`,
      column: `${idPrefix}-box-column`,
      depth: `${idPrefix}-box-depth`,
      experiments: `${idPrefix}-box-experiments`,
      comments: `${idPrefix}-box-comments`,
    }),
    [idPrefix],
  );
  const [formValues, setFormValues] = useState<BoxFormValues>(EMPTY_FORM);
  const [options, setOptions] = useState<BoxOptionsResponse | null>(null);
  const [optionsLoading, setOptionsLoading] = useState(false);
  const [optionsError, setOptionsError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!open) {
      return;
    }
    setFormValues(EMPTY_FORM);
    setSubmitError(null);
  }, [open]);

  useEffect(() => {
    if (!open) {
      return;
    }
    let isActive = true;
    const loadOptions = async () => {
      setOptionsLoading(true);
      setOptionsError(null);
      try {
        const response = await fetch("/api/dashboard/boxes/options", { cache: "no-store" });
        if (!response.ok) {
          throw new Error("Unable to load box form options.");
        }
        const payload = (await response.json()) as BoxOptionsResponse;
        if (isActive) {
          setOptions(payload);
        }
      } catch (error) {
        if (isActive) {
          const message =
            error instanceof Error ? error.message : "Unable to load box form options.";
          setOptionsError(message);
        }
      } finally {
        if (isActive) {
          setOptionsLoading(false);
        }
      }
    };

    void loadOptions();

    return () => {
      isActive = false;
    };
  }, [open]);

  const isReady = useMemo(() => Boolean(options && !optionsLoading), [options, optionsLoading]);

  const handleInputChange = (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
    field: keyof BoxFormValues,
  ) => {
    setFormValues((previous) => ({
      ...previous,
      [field]: event.target.value,
    }));
  };

  const handleSelectChange = (field: keyof BoxFormValues, value: string) => {
    setFormValues((previous) => ({
      ...previous,
      [field]: value === EMPTY_SELECT_VALUE ? "" : value,
    }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitError(null);

    if (!formValues.box_id.trim() || !formValues.box_type || !formValues.location) {
      setSubmitError("Box ID, box type, and location are required.");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        box_id: formValues.box_id.trim(),
        box_type: formValues.box_type,
        location: formValues.location,
        row: normaliseNullable(formValues.row),
        column: normaliseNullable(formValues.column),
        depth: normaliseNullable(formValues.depth),
        comments: normaliseNullable(formValues.comments),
        experiments: formValues.experiments.map((value) => Number(value)),
      };

      const response = await fetch("/api/dashboard/boxes", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => null);
        throw new Error(formatErrorMessage(errorPayload));
      }

      setFormValues(EMPTY_FORM);
      onCreated();
      onOpenChange(false);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to create the box.";
      setSubmitError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New Box</DialogTitle>
          <DialogDescription>Enter the new box details and save to register it.</DialogDescription>
        </DialogHeader>

        {optionsError ? (
          <AlertError>
            <AlertDescription>{optionsError}</AlertDescription>
          </AlertError>
        ) : null}

        {submitError ? (
          <AlertError>
            <AlertDescription>{submitError}</AlertDescription>
          </AlertError>
        ) : null}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <label htmlFor={fieldIds.boxId} className="space-y-2 text-sm">
              <span className="font-medium">Box ID *</span>
              <Input
                id={fieldIds.boxId}
                value={formValues.box_id}
                onChange={(event) => handleInputChange(event, "box_id")}
                placeholder="e.g. BOX-001"
                required
              />
            </label>

            <label htmlFor={fieldIds.boxType} className="space-y-2 text-sm">
              <span className="font-medium">Box type *</span>
              <Select
                value={formValues.box_type}
                onValueChange={(value) => handleSelectChange("box_type", value)}
                disabled={!isReady}
              >
                <SelectTrigger id={fieldIds.boxType} className="w-full">
                  <SelectValue placeholder="Select box type" />
                </SelectTrigger>
                <SelectContent>
                  {options?.box_type_options.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>

            <label htmlFor={fieldIds.location} className="space-y-2 text-sm">
              <span className="font-medium">Location *</span>
              <Select
                value={formValues.location}
                onValueChange={(value) => handleSelectChange("location", value)}
                disabled={!isReady}
              >
                <SelectTrigger id={fieldIds.location} className="w-full">
                  <SelectValue placeholder="Select location" />
                </SelectTrigger>
                <SelectContent>
                  {options?.location_options.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>

            <label htmlFor={fieldIds.row} className="space-y-2 text-sm">
              <span className="font-medium">Row</span>
              <Select
                value={formValues.row || EMPTY_SELECT_VALUE}
                onValueChange={(value) => handleSelectChange("row", value)}
                disabled={!isReady}
              >
                <SelectTrigger id={fieldIds.row} className="w-full">
                  <SelectValue placeholder="None" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>None</SelectItem>
                  {options?.row_options.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>

            <label htmlFor={fieldIds.column} className="space-y-2 text-sm">
              <span className="font-medium">Column</span>
              <Select
                value={formValues.column || EMPTY_SELECT_VALUE}
                onValueChange={(value) => handleSelectChange("column", value)}
                disabled={!isReady}
              >
                <SelectTrigger id={fieldIds.column} className="w-full">
                  <SelectValue placeholder="None" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>None</SelectItem>
                  {options?.column_options.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>

            <label htmlFor={fieldIds.depth} className="space-y-2 text-sm">
              <span className="font-medium">Depth</span>
              <Select
                value={formValues.depth || EMPTY_SELECT_VALUE}
                onValueChange={(value) => handleSelectChange("depth", value)}
                disabled={!isReady}
              >
                <SelectTrigger id={fieldIds.depth} className="w-full">
                  <SelectValue placeholder="None" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={EMPTY_SELECT_VALUE}>None</SelectItem>
                  {options?.depth_options.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
          </div>

          <div className="space-y-2 text-sm">
            <label htmlFor={fieldIds.experiments} className="font-medium">
              Experiments
            </label>
            <MultiSelect
              values={formValues.experiments}
              onValuesChange={(values) =>
                setFormValues((previous) => ({
                  ...previous,
                  experiments: values,
                }))
              }
            >
              <MultiSelectTrigger id={fieldIds.experiments} className="w-full justify-between">
                <MultiSelectValue placeholder="Select experiments" />
              </MultiSelectTrigger>
              <MultiSelectContent search={{ placeholder: "Search experiments..." }}>
                {options?.experiments.map((experiment) => (
                  <MultiSelectItem key={experiment.id} value={String(experiment.id)}>
                    {experiment.label}
                  </MultiSelectItem>
                ))}
              </MultiSelectContent>
            </MultiSelect>
          </div>

          <div className="space-y-2 pb-2 text-sm">
            <label htmlFor={fieldIds.comments} className="font-medium">
              Comments
            </label>
            <Textarea
              id={fieldIds.comments}
              value={formValues.comments}
              onChange={(event) => handleInputChange(event, "comments")}
              placeholder="Add any notes about this box."
            />
          </div>

          <DialogFooter className="gap-2 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={!isReady || isSubmitting}>
              {isSubmitting ? "Saving..." : "Save Box"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
