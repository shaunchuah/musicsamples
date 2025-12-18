// frontend/components/users/user-options.ts
// Provides the select options and enums for user job titles and organisations.
// Exists so the table and form share a single source of option labels and values.

import { z } from "zod";

export const JOB_TITLE_OPTIONS = [
  { value: "", label: "Select job title" },
  { value: "research_assistant", label: "Research Assistant" },
  { value: "postdoctoral_researcher", label: "Postdoctoral Researcher" },
  { value: "phd_student", label: "PhD Student" },
  { value: "clinical_research_fellow", label: "Clinical Research Fellow" },
  { value: "clinical_research_nurse", label: "Clinical Research Nurse" },
  { value: "clinician_scientist", label: "Clinician Scientist" },
  { value: "scientist", label: "Scientist" },
  { value: "unknown", label: "Unknown" },
];

export const PRIMARY_ORG_OPTIONS = [
  { value: "", label: "Select primary organisation" },
  { value: "nhs_lothian", label: "NHS Lothian" },
  { value: "nhs_ggc", label: "NHS GGC" },
  { value: "nhs_tayside", label: "NHS Tayside" },
  { value: "university_of_edinburgh", label: "University of Edinburgh" },
  { value: "university_of_glasgow", label: "University of Glasgow" },
  { value: "university_of_dundee", label: "University of Dundee" },
  { value: "unknown", label: "Unknown" },
];

export const jobTitleEnum = z.enum(
  JOB_TITLE_OPTIONS.filter((option) => option.value).map((option) => option.value) as [
    string,
    ...string[],
  ],
);

export const primaryOrgEnum = z.enum(
  PRIMARY_ORG_OPTIONS.filter((option) => option.value).map((option) => option.value) as [
    string,
    ...string[],
  ],
);

export function optionLabel(
  options: { value: string; label: string }[],
  value: string | null | undefined,
): string {
  if (!value) return "—";
  const match = options.find((option) => option.value === value);
  return match?.label ?? value;
}
