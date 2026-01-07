// frontend/components/study-ids/study-id-samples-card.tsx
// Displays a card containing the filtered samples table for a specific study identifier.
// Exists so the Study ID detail page can reuse the existing SamplesTable while scoping it to linked samples only.

"use client";

import { SamplesTable } from "@/components/samples/samples-table";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

type StudyIdSamplesCardProps = {
  studyIdName: string;
};

export function StudyIdSamplesCard({ studyIdName }: StudyIdSamplesCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Linked samples</CardTitle>
        <CardDescription>Samples associated with this study identifier.</CardDescription>
      </CardHeader>
      <CardContent className="overflow-auto">
        <SamplesTable initialFilters={{ study_id__name: studyIdName }} hideToolbar />
      </CardContent>
    </Card>
  );
}
