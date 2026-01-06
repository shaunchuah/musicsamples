// frontend/components/ui/table-pagination.tsx
// Wraps PaginationControls with shared table pagination calculations.
// Exists to keep pagination math consistent across dashboard tables.

"use client";

import { PaginationControls } from "@/components/ui/pagination-controls";

type TablePaginationProps = {
  canPrevious: boolean;
  canNext: boolean;
  isLoading: boolean;
  onPrevious: () => void;
  onNext: () => void;
  pageIndex: number;
  pageSize: number;
  pageCount: number;
  currentCount: number;
  totalCount: number | null;
  itemLabel: string;
};

export function TablePagination({
  canPrevious,
  canNext,
  isLoading,
  onPrevious,
  onNext,
  pageIndex,
  pageSize,
  pageCount,
  currentCount,
  totalCount,
  itemLabel,
}: TablePaginationProps) {
  const firstItemIndex = currentCount > 0 ? (pageIndex - 1) * pageSize + 1 : 0;
  const lastItemIndex = currentCount > 0 ? (pageIndex - 1) * pageSize + currentCount : 0;
  const totalLabel = totalCount ?? "unknown";

  return (
    <PaginationControls
      canPrevious={canPrevious}
      canNext={canNext}
      isLoading={isLoading}
      onPrevious={onPrevious}
      onNext={onNext}
      pageIndex={pageIndex}
      pageCount={pageCount}
      firstItemIndex={firstItemIndex}
      lastItemIndex={lastItemIndex}
      totalLabel={totalLabel}
      itemLabel={itemLabel}
    />
  );
}
