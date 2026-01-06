// frontend/components/boxes/box-edit-dialog-button.tsx
// Renders an edit button that opens the box form dialog in edit mode.
// Exists to reuse the modal edit workflow from box detail views without duplicating form logic.

"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { BoxFormDialog } from "@/components/boxes/box-form-dialog";
import { Button } from "@/components/ui/button";

type BoxEditDialogButtonProps = {
  box: {
    id: number;
    box_id: string;
    basic_science_group: string;
    box_type: string;
    location: string;
    row: string | null;
    column: string | null;
    depth: string | null;
    comments: string | null;
    experiments: { id: number }[];
  };
};

export function BoxEditDialogButton({ box }: BoxEditDialogButtonProps) {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  return (
    <>
      <BoxFormDialog
        open={open}
        onOpenChange={setOpen}
        onUpdated={() => router.refresh()}
        mode="edit"
        boxId={box.id}
        initialValues={{
          box_id: box.box_id,
          basic_science_group: box.basic_science_group,
          box_type: box.box_type,
          location: box.location,
          row: box.row,
          column: box.column,
          depth: box.depth,
          comments: box.comments,
          experiments: box.experiments.map((experiment) => experiment.id),
        }}
      />
      <Button type="button" onClick={() => setOpen(true)} className="w-full sm:w-auto">
        Edit box
      </Button>
    </>
  );
}
