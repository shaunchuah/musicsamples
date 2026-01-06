// frontend/components/users/user-form-dialog.tsx
// Renders the create/edit user form dialog with validation and submission handling.
// Exists to keep the users table lean while reusing the same dialog across actions.

import { zodResolver } from "@hookform/resolvers/zod";
import { useCallback, useEffect, useId, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

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
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
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

import {
  JOB_TITLE_OPTIONS,
  jobTitleEnum,
  PRIMARY_ORG_OPTIONS,
  primaryOrgEnum,
} from "./user-options";
import type { StaffUser, UserFormValues } from "./user-types";

const dialogSchema = z.object({
  email: z.string().email("Enter a valid email."),
  first_name: z.string().min(1, "First name is required."),
  last_name: z.string().min(1, "Last name is required."),
  job_title: z.union([z.literal(""), jobTitleEnum]),
  primary_organisation: z.union([z.literal(""), primaryOrgEnum]),
  groups: z.array(z.string()),
});

const EMPTY_SELECT_VALUE = "__none__";

function normalisePayload(values: UserFormValues): UserFormValues {
  return {
    ...values,
    job_title: values.job_title?.trim() ?? "",
    primary_organisation: values.primary_organisation?.trim() ?? "",
    groups: Array.from(new Set(values.groups ?? [])).filter(Boolean),
  };
}

type UserFormDialogProps = {
  mode: "create" | "edit";
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultValues: StaffUser | null;
  onSubmit: (values: UserFormValues, userId?: number) => Promise<void>;
  groupOptions: string[];
  groupsLoading: boolean;
  groupsError: string | null;
};

export function UserFormDialog({
  mode,
  open,
  onOpenChange,
  defaultValues,
  onSubmit,
  groupOptions,
  groupsLoading,
  groupsError,
}: UserFormDialogProps) {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const jobTitleId = useId();
  const primaryOrgId = useId();
  const groupsId = useId();

  const form = useForm<UserFormValues>({
    resolver: zodResolver(dialogSchema),
    defaultValues: {
      email: "",
      first_name: "",
      last_name: "",
      job_title: "",
      primary_organisation: "",
      groups: [],
    },
  });

  useEffect(() => {
    form.reset({
      email: defaultValues?.email ?? "",
      first_name: defaultValues?.first_name ?? "",
      last_name: defaultValues?.last_name ?? "",
      job_title: defaultValues?.job_title ?? "",
      primary_organisation: defaultValues?.primary_organisation ?? "",
      groups: defaultValues?.groups ?? [],
    });
    setSubmitError(null);
  }, [defaultValues, form, open]);

  const handleSubmit = useCallback(
    async (values: UserFormValues) => {
      setSubmitError(null);
      try {
        await onSubmit(normalisePayload(values), defaultValues?.id);
        onOpenChange(false);
      } catch (error) {
        const message = error instanceof Error ? error.message : "Unable to save user.";
        setSubmitError(message);
      }
    },
    [defaultValues?.id, onOpenChange, onSubmit],
  );

  const isSubmitting = form.formState.isSubmitting;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{mode === "create" ? "Add New User" : "Edit User"}</DialogTitle>
          <DialogDescription>
            {mode === "create"
              ? "Create a new account for a team member. A welcome email will be sent automatically."
              : "Update the user details shown in the management table."}
          </DialogDescription>
        </DialogHeader>

        {submitError ? (
          <AlertError>
            <AlertDescription>{submitError}</AlertDescription>
          </AlertError>
        ) : null}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      autoComplete="email"
                      placeholder="user@example.com"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>First name</FormLabel>
                    <FormControl>
                      <Input autoComplete="given-name" placeholder="First name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="last_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Last name</FormLabel>
                    <FormControl>
                      <Input autoComplete="family-name" placeholder="Last name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="job_title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel htmlFor={jobTitleId}>Job title</FormLabel>
                  <FormControl>
                    <Select
                      value={field.value || EMPTY_SELECT_VALUE}
                      onValueChange={(value) =>
                        field.onChange(value === EMPTY_SELECT_VALUE ? "" : value)
                      }
                    >
                      <SelectTrigger id={jobTitleId} className="w-full">
                        <SelectValue
                          placeholder={JOB_TITLE_OPTIONS[0]?.label ?? "Select job title"}
                        />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={EMPTY_SELECT_VALUE}>
                          {JOB_TITLE_OPTIONS[0]?.label ?? "Select job title"}
                        </SelectItem>
                        {JOB_TITLE_OPTIONS.filter((option) => option.value).map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="primary_organisation"
              render={({ field }) => (
                <FormItem>
                  <FormLabel htmlFor={primaryOrgId}>Primary organisation</FormLabel>
                  <FormControl>
                    <Select
                      value={field.value || EMPTY_SELECT_VALUE}
                      onValueChange={(value) =>
                        field.onChange(value === EMPTY_SELECT_VALUE ? "" : value)
                      }
                    >
                      <SelectTrigger id={primaryOrgId} className="w-full">
                        <SelectValue
                          placeholder={
                            PRIMARY_ORG_OPTIONS[0]?.label ?? "Select primary organisation"
                          }
                        />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={EMPTY_SELECT_VALUE}>
                          {PRIMARY_ORG_OPTIONS[0]?.label ?? "Select primary organisation"}
                        </SelectItem>
                        {PRIMARY_ORG_OPTIONS.filter((option) => option.value).map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="groups"
              render={({ field }) => (
                <FormItem>
                  <FormLabel htmlFor={groupsId}>Groups</FormLabel>
                  <FormControl>
                    <div className="space-y-2">
                      <MultiSelect
                        values={field.value ?? []}
                        onValuesChange={(values) => field.onChange(values)}
                      >
                        <MultiSelectTrigger
                          id={groupsId}
                          className="w-full justify-between"
                          disabled={groupsLoading || !groupOptions.length}
                        >
                          <MultiSelectValue placeholder="Select groups" />
                        </MultiSelectTrigger>
                        <MultiSelectContent search={{ placeholder: "Search groups..." }}>
                          {groupOptions.map((groupName) => (
                            <MultiSelectItem key={groupName} value={groupName}>
                              {groupName}
                            </MultiSelectItem>
                          ))}
                        </MultiSelectContent>
                      </MultiSelect>
                      {groupsLoading ? (
                        <p className="text-sm text-muted-foreground">Loading groups...</p>
                      ) : null}
                      {!groupsLoading && !groupOptions.length ? (
                        <p className="text-sm text-muted-foreground">No groups available.</p>
                      ) : null}
                      {groupsError ? (
                        <p className="text-sm text-destructive">{groupsError}</p>
                      ) : null}
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Saving..." : mode === "create" ? "Create user" : "Save changes"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
