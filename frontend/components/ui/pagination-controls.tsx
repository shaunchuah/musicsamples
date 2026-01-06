// frontend/components/ui/pagination-controls.tsx
// Shared pagination controls for dashboard tables with "Showing" and page navigation text.
// Exists to keep pagination layout consistent across samples, boxes, and experiments tables.

"use client";

import { Button } from "@/components/ui/button";

type PaginationControlsProps = {
  canPrevious: boolean;
  canNext: boolean;
  isLoading: boolean;
  onPrevious: () => void;
  onNext: () => void;
  pageIndex: number;
  pageCount: number;
  firstItemIndex: number;
  lastItemIndex: number;
  totalLabel: number | string;
  itemLabel: string;
};

export function PaginationControls({
  canPrevious,
  canNext,
  isLoading,
  onPrevious,
  onNext,
  pageIndex,
  pageCount,
  firstItemIndex,
  lastItemIndex,
  totalLabel,
  itemLabel,
}: PaginationControlsProps) {
  return (
    <div className="flex flex-col gap-2 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
      <p>
        Showing {firstItemIndex === 0 ? 0 : firstItemIndex}-{lastItemIndex} of {totalLabel}{" "}
        {itemLabel}
      </p>
      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={onPrevious}
          disabled={!canPrevious || isLoading}
        >
          Previous
        </Button>
        <span>
          Page {pageCount === 0 ? 0 : pageIndex}
          {pageCount > 0 ? ` of ${pageCount}` : ""}
        </span>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={onNext}
          disabled={!canNext || isLoading}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
