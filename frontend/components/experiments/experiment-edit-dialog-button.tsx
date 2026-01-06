// frontend/components/experiments/experiment-edit-dialog-button.tsx
// Renders an edit button that opens the experiment form dialog in edit mode.
// Exists to reuse the modal edit workflow from experiment detail views without duplicating form logic.

"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { ExperimentFormDialog } from "@/components/experiments/experiment-form-dialog";
import { Button } from "@/components/ui/button";

type ExperimentEditDialogButtonProps = {
  experiment: {
    id: number;
    basic_science_group: string;
    name: string;
    description: string | null;
    date: string | null;
    species: string;
    sample_types: number[];
    tissue_types: number[];
  };
};

export function ExperimentEditDialogButton({ experiment }: ExperimentEditDialogButtonProps) {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  return (
    <>
      <ExperimentFormDialog
        open={open}
        onOpenChange={setOpen}
        onUpdated={() => router.refresh()}
        mode="edit"
        experimentId={experiment.id}
        initialValues={{
          basic_science_group: experiment.basic_science_group,
          name: experiment.name,
          description: experiment.description,
          date: experiment.date,
          species: experiment.species,
          sample_types: experiment.sample_types,
          tissue_types: experiment.tissue_types,
        }}
      />
      <Button type="button" onClick={() => setOpen(true)} className="w-full sm:w-auto">
        Edit experiment
      </Button>
    </>
  );
}
