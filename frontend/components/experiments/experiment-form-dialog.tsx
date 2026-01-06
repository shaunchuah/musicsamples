// frontend/components/experiments/experiment-form-dialog.tsx
// Renders the modal form used to create or edit an experiment from the dashboard.
// Exists to keep the experiments table focused while providing a dedicated experiment editing workflow.

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

type ExperimentOption = {
  value: string;
  label: string;
};

type ExperimentOptionsResponse = {
  basic_science_group_options: ExperimentOption[];
  species_options: ExperimentOption[];
  sample_types: ExperimentOption[];
  tissue_types: ExperimentOption[];
};

type ExperimentFormValues = {
  basic_science_group: string;
  name: string;
  description: string;
  date: string;
  species: string;
  sample_types: string[];
  tissue_types: string[];
};

export type ExperimentFormInitialValues = {
  basic_science_group?: string | null;
  name?: string | null;
  description?: string | null;
  date?: string | null;
  species?: string | null;
  sample_types?: Array<number | string>;
  tissue_types?: Array<number | string>;
};

type ExperimentFormDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated?: () => void;
  onUpdated?: () => void;
  mode?: "create" | "edit";
  experimentId?: number | string | null;
  initialValues?: ExperimentFormInitialValues;
};

const EMPTY_FORM: ExperimentFormValues = {
  basic_science_group: "",
  name: "",
  description: "",
  date: "",
  species: "",
  sample_types: [],
  tissue_types: [],
};

function normaliseNullable(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function formatErrorMessage(payload: unknown, actionLabel: string) {
  if (!payload || typeof payload !== "object") {
    return `Unable to ${actionLabel} the experiment. Please try again.`;
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
  return entries.length
    ? entries.join(" ")
    : `Unable to ${actionLabel} the experiment. Please try again.`;
}

function normaliseInitialValues(values?: ExperimentFormInitialValues | null): ExperimentFormValues {
  return {
    basic_science_group: values?.basic_science_group ?? "",
    name: values?.name ?? "",
    description: values?.description ?? "",
    date: values?.date ?? "",
    species: values?.species ?? "",
    sample_types: values?.sample_types ? values.sample_types.map((value) => String(value)) : [],
    tissue_types: values?.tissue_types ? values.tissue_types.map((value) => String(value)) : [],
  };
}

export function ExperimentFormDialog({
  open,
  onOpenChange,
  onCreated,
  onUpdated,
  mode = "create",
  experimentId,
  initialValues,
}: ExperimentFormDialogProps) {
  const idPrefix = useId();
  const fieldIds = useMemo(
    () => ({
      basicScienceGroup: `${idPrefix}-experiment-basic-science-group`,
      name: `${idPrefix}-experiment-name`,
      description: `${idPrefix}-experiment-description`,
      date: `${idPrefix}-experiment-date`,
      species: `${idPrefix}-experiment-species`,
      sampleTypes: `${idPrefix}-experiment-sample-types`,
      tissueTypes: `${idPrefix}-experiment-tissue-types`,
    }),
    [idPrefix],
  );
  const [formValues, setFormValues] = useState<ExperimentFormValues>(EMPTY_FORM);
  const [options, setOptions] = useState<ExperimentOptionsResponse | null>(null);
  const [optionsLoading, setOptionsLoading] = useState(false);
  const [optionsError, setOptionsError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isEditMode = mode === "edit";

  useEffect(() => {
    if (!open) {
      return;
    }
    if (isEditMode) {
      setFormValues(normaliseInitialValues(initialValues));
    } else {
      setFormValues(EMPTY_FORM);
    }
    setSubmitError(null);
  }, [initialValues, isEditMode, open]);

  useEffect(() => {
    if (!open) {
      return;
    }
    let isActive = true;
    const loadOptions = async () => {
      setOptionsLoading(true);
      setOptionsError(null);
      try {
        const response = await fetch("/api/dashboard/experiments/options", { cache: "no-store" });
        if (!response.ok) {
          throw new Error("Unable to load experiment form options.");
        }
        const payload = (await response.json()) as ExperimentOptionsResponse;
        if (isActive) {
          setOptions(payload);
        }
      } catch (error) {
        if (isActive) {
          const message =
            error instanceof Error ? error.message : "Unable to load experiment form options.";
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
    field: keyof ExperimentFormValues,
  ) => {
    setFormValues((previous) => ({
      ...previous,
      [field]: event.target.value,
    }));
  };

  const handleSelectChange = (field: keyof ExperimentFormValues, value: string) => {
    setFormValues((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitError(null);

    if (!formValues.basic_science_group || !formValues.name.trim() || !formValues.species) {
      setSubmitError("Experiment name, group, and species are required.");
      return;
    }

    setIsSubmitting(true);
    try {
      if (isEditMode && !experimentId) {
        throw new Error("Missing experiment identifier.");
      }
      const payload = {
        basic_science_group: formValues.basic_science_group,
        name: formValues.name.trim(),
        description: normaliseNullable(formValues.description),
        date: normaliseNullable(formValues.date),
        species: formValues.species,
        sample_types: formValues.sample_types.map((value) => Number(value)),
        tissue_types: formValues.tissue_types.map((value) => Number(value)),
      };

      const response = await fetch(
        isEditMode ? `/api/dashboard/experiments/${experimentId}` : "/api/dashboard/experiments",
        {
          method: isEditMode ? "PATCH" : "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        },
      );

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => null);
        const actionLabel = isEditMode ? "update" : "create";
        throw new Error(formatErrorMessage(errorPayload, actionLabel));
      }

      if (isEditMode) {
        onUpdated?.();
        onOpenChange(false);
      } else {
        setFormValues(EMPTY_FORM);
        onCreated?.();
        onOpenChange(false);
      }
    } catch (error) {
      const fallbackLabel = isEditMode ? "update" : "create";
      const message =
        error instanceof Error ? error.message : `Unable to ${fallbackLabel} the experiment.`;
      setSubmitError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const dialogTitle = isEditMode ? "Edit Experiment" : "Add New Experiment";
  const dialogDescription = isEditMode
    ? "Update the experiment details and save your changes."
    : "Enter the new experiment details and save to register it.";
  const submitLabel = isEditMode ? "Save Changes" : "Save Experiment";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{dialogTitle}</DialogTitle>
          <DialogDescription>{dialogDescription}</DialogDescription>
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
            <label htmlFor={fieldIds.name} className="space-y-2 text-sm">
              <span className="font-medium">Experiment Name *</span>
              <Input
                id={fieldIds.name}
                value={formValues.name}
                onChange={(event) => handleInputChange(event, "name")}
                placeholder="e.g. EXP-001"
                required
              />
            </label>

            <label htmlFor={fieldIds.basicScienceGroup} className="space-y-2 text-sm">
              <span className="font-medium">Group *</span>
              <Select
                value={formValues.basic_science_group}
                onValueChange={(value) => handleSelectChange("basic_science_group", value)}
                disabled={!isReady}
              >
                <SelectTrigger id={fieldIds.basicScienceGroup} className="w-full">
                  <SelectValue placeholder="Select group" />
                </SelectTrigger>
                <SelectContent>
                  {options?.basic_science_group_options.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>

            <label htmlFor={fieldIds.species} className="space-y-2 text-sm">
              <span className="font-medium">Species *</span>
              <Select
                value={formValues.species}
                onValueChange={(value) => handleSelectChange("species", value)}
                disabled={!isReady}
              >
                <SelectTrigger id={fieldIds.species} className="w-full">
                  <SelectValue placeholder="Select species" />
                </SelectTrigger>
                <SelectContent>
                  {options?.species_options.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>

            <label htmlFor={fieldIds.date} className="space-y-2 text-sm">
              <span className="font-medium">Experiment Date</span>
              <Input
                id={fieldIds.date}
                type="date"
                value={formValues.date}
                onChange={(event) => handleInputChange(event, "date")}
              />
            </label>
          </div>

          <div className="space-y-2 text-sm">
            <label htmlFor={fieldIds.sampleTypes} className="font-medium">
              Sample Types
            </label>
            <MultiSelect
              values={formValues.sample_types}
              onValuesChange={(values) =>
                setFormValues((previous) => ({
                  ...previous,
                  sample_types: values,
                }))
              }
            >
              <MultiSelectTrigger id={fieldIds.sampleTypes} className="w-full justify-between">
                <MultiSelectValue placeholder="Select sample types" />
              </MultiSelectTrigger>
              <MultiSelectContent search={{ placeholder: "Search sample types..." }}>
                {options?.sample_types.map((sampleType) => (
                  <MultiSelectItem key={sampleType.value} value={sampleType.value}>
                    {sampleType.label}
                  </MultiSelectItem>
                ))}
              </MultiSelectContent>
            </MultiSelect>
          </div>

          <div className="space-y-2 text-sm">
            <label htmlFor={fieldIds.tissueTypes} className="font-medium">
              Tissue Types
            </label>
            <MultiSelect
              values={formValues.tissue_types}
              onValuesChange={(values) =>
                setFormValues((previous) => ({
                  ...previous,
                  tissue_types: values,
                }))
              }
            >
              <MultiSelectTrigger id={fieldIds.tissueTypes} className="w-full justify-between">
                <MultiSelectValue placeholder="Select tissue types" />
              </MultiSelectTrigger>
              <MultiSelectContent search={{ placeholder: "Search tissue types..." }}>
                {options?.tissue_types.map((tissueType) => (
                  <MultiSelectItem key={tissueType.value} value={tissueType.value}>
                    {tissueType.label}
                  </MultiSelectItem>
                ))}
              </MultiSelectContent>
            </MultiSelect>
          </div>

          <div className="space-y-2 pb-2 text-sm">
            <label htmlFor={fieldIds.description} className="font-medium">
              Description
            </label>
            <Textarea
              id={fieldIds.description}
              value={formValues.description}
              onChange={(event) => handleInputChange(event, "description")}
              placeholder="Add notes about this experiment."
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
              {isSubmitting ? "Saving..." : submitLabel}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
