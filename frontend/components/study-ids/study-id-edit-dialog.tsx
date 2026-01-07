// frontend/components/study-ids/study-id-edit-dialog.tsx
// Provides the reusable study ID edit dialog used by list and detail views.
// Exists to prevent each study ID surface from reimplementing the same edit modal UX.

"use client";

import { useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { useCallback, useId, useState } from "react";

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
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type StudyIdEditDialogProps = {
  studyId: {
    id: number;
    name: string;
    study_name: string | null;
  };
  onSaved?: () => void;
  refreshOnSave?: boolean;
  renderTrigger?: (options: { open: () => void }) => ReactNode;
  triggerLabel?: string;
};

const STUDY_NAME_UNSET_VALUE = "__unset_study_name__";

const STUDY_NAME_OPTIONS = [
  { value: STUDY_NAME_UNSET_VALUE, label: "Unspecified" },
  { value: "gidamps", label: "GI-DAMPs" },
  { value: "music", label: "MUSIC" },
  { value: "mini_music", label: "Mini-MUSIC" },
  { value: "marvel", label: "MARVEL" },
  { value: "fate_cd", label: "FATE-CD" },
  { value: "none", label: "None" },
];

const STUDY_NAME_SELECT_OPTIONS = STUDY_NAME_OPTIONS.filter(
  (option) => option.value.trim().length > 0,
);

export function StudyIdEditDialog({
  studyId,
  onSaved,
  refreshOnSave = false,
  renderTrigger,
  triggerLabel,
}: StudyIdEditDialogProps) {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [editForm, setEditForm] = useState({
    name: "",
    study_name: STUDY_NAME_UNSET_VALUE,
  });
  const [editFieldErrors, setEditFieldErrors] = useState<Record<string, string>>({});
  const [editErrorMessage, setEditErrorMessage] = useState<string | null>(null);
  const studyIdInputId = useId();
  const studyNameSelectId = useId();

  const openDialog = useCallback(() => {
    setEditFieldErrors({});
    setEditErrorMessage(null);
    setEditForm({
      name: studyId.name,
      study_name: studyId.study_name ?? STUDY_NAME_UNSET_VALUE,
    });
    setIsOpen(true);
  }, [studyId]);

  const triggerLabelToUse = triggerLabel ?? "Edit study ID";
  const renderTriggerContent =
    renderTrigger ??
    (({ open }: { open: () => void }) => (
      <Button size="sm" onClick={open}>
        {triggerLabelToUse}
      </Button>
    ));

  const closeDialog = useCallback(() => {
    if (isSaving) {
      return;
    }
    setIsOpen(false);
  }, [isSaving]);

  const handleEditFieldChange = useCallback((field: keyof typeof editForm, value: string) => {
    setEditForm((previous) => ({ ...previous, [field]: value }));
    setEditFieldErrors((errors) => ({ ...errors, [field]: "" }));
    setEditErrorMessage(null);
  }, []);

  const submitEditForm = useCallback(async () => {
    setIsSaving(true);
    setEditFieldErrors({});
    setEditErrorMessage(null);

    try {
      const response = await fetch(`/api/dashboard/study-ids/${studyId.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: editForm.name,
          study_name:
            editForm.study_name === STUDY_NAME_UNSET_VALUE ? null : editForm.study_name || null,
        }),
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        if (payload && typeof payload === "object") {
          const fieldErrors: Record<string, string> = {};
          Object.entries(payload).forEach(([key, value]) => {
            if (Array.isArray(value)) {
              fieldErrors[key] = value.join(" ");
            } else if (typeof value === "string") {
              fieldErrors[key] = value;
            }
          });
          if (Object.keys(fieldErrors).length > 0) {
            setEditFieldErrors(fieldErrors);
          }
          if (typeof payload.detail === "string") {
            setEditErrorMessage(payload.detail);
          }
        } else {
          setEditErrorMessage("Unable to update study ID.");
        }
        return;
      }

      onSaved?.();
      if (refreshOnSave) {
        router.refresh();
      }
      setIsOpen(false);
    } catch {
      setEditErrorMessage("Unable to update study ID.");
    } finally {
      setIsSaving(false);
    }
  }, [editForm.name, editForm.study_name, onSaved, refreshOnSave, router, studyId.id]);

  return (
    <>
      {renderTriggerContent({ open: openDialog })}
      <Dialog
        open={isOpen}
        onOpenChange={(open) => {
          if (!open) {
            closeDialog();
            return;
          }
          setIsOpen(true);
        }}
      >
        <DialogContent showCloseButton={!isSaving}>
          <DialogHeader>
            <DialogTitle>Edit study ID</DialogTitle>
            <DialogDescription>
              Update the identifier and study name associated with this record.
            </DialogDescription>
          </DialogHeader>
          {editErrorMessage ? (
            <p className="rounded-md border border-destructive/50 bg-destructive/5 px-3 py-2 text-sm text-destructive">
              {editErrorMessage}
            </p>
          ) : null}
          <div className="space-y-4 pt-2 text-sm">
            <div className="space-y-1">
              <Label htmlFor={studyIdInputId}>Study ID</Label>
              <Input
                id={studyIdInputId}
                value={editForm.name}
                onChange={(event) => handleEditFieldChange("name", event.target.value)}
              />
              {editFieldErrors.name ? (
                <p className="text-sm text-destructive">{editFieldErrors.name}</p>
              ) : null}
            </div>
            <div className="space-y-1">
              <Label htmlFor={studyNameSelectId}>Study Name</Label>
              <Select
                value={editForm.study_name || STUDY_NAME_UNSET_VALUE}
                onValueChange={(value) => handleEditFieldChange("study_name", value)}
              >
                <SelectTrigger id={studyNameSelectId}>
                  <SelectValue placeholder="Select study name" />
                </SelectTrigger>
                <SelectContent>
                  {STUDY_NAME_SELECT_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {editFieldErrors.study_name ? (
                <p className="text-sm text-destructive">{editFieldErrors.study_name}</p>
              ) : null}
            </div>
          </div>
          <DialogFooter className="justify-end gap-2">
            <Button variant="outline" onClick={closeDialog} disabled={isSaving}>
              Cancel
            </Button>
            <Button onClick={submitEditForm} disabled={isSaving}>
              {isSaving ? "Saving…" : "Save changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
