"use client";

import { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type Sample = {
  id: number;
  study_name: string;
  sample_id: string;
  patient_id: string;
  sample_location: string;
  sample_sublocation: string;
  sample_type: string;
  sample_datetime: string;
  sample_comments: string;
  is_used: boolean;
  music_timepoint: string;
  marvel_timepoint: string;
  processing_datetime: string;
  frozen_datetime: string;
  sample_volume: number | null;
  sample_volume_units: string;
  freeze_thaw_count: number | null;
  haemolysis_reference: string;
  biopsy_location: string;
  biopsy_inflamed_status: string;
  qubit_cfdna_ng_ul: number | null;
  paraffin_block_key: string | null;
  created: string;
  created_by: string;
  last_modified: string;
  last_modified_by: string;
};

export const columns: ColumnDef<Sample>[] = [
  {
    accessorKey: "study_name",
    header: "Study Name",
    cell: ({ row }) => {
      const study_name = row.original.study_name;
      const studyNameMap: Record<string, string> = {
        music: "MUSIC",
        mini_music: "Mini-MUSIC",
        marvel: "MARVEL",
        mini_marvel: "Mini-MARVEL",
        none: "None",
      };
      return <div>{studyNameMap[study_name.toLowerCase()] || study_name}</div>;
    },
  },
  {
    accessorKey: "sample_id",
    header: "Sample ID",
  },
  {
    accessorKey: "patient_id",
    header: "Patient ID",
  },
  {
    accessorKey: "sample_location",
    header: "Location",
  },
  {
    accessorKey: "sample_sublocation",
    header: "Sublocation",
  },
  {
    accessorKey: "sample_type",
    header: "Type",
  },
  {
    accessorKey: "sample_datetime",
    header: "Date/Time",
    cell: ({ row }) => {
      const date = new Date(row.original.sample_datetime);
      const formatted = date.toLocaleString("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });

      return <div>{formatted}</div>;
    },
  },
  {
    accessorKey: "sample_comments",
    header: "Comments",
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const payment = row.original;

      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>View sample</DropdownMenuItem>
            <DropdownMenuItem>Edit sample</DropdownMenuItem>
            <DropdownMenuItem>Use sample</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];
