/*
 * frontend/components/ui/detail-header.tsx
 *
 * Description: Reusable header component for detail pages. Renders an optional
 * category label, a main title, an optional subtitle, and an actions slot on
 * the right side.
 *
 * Why: To provide a consistent, accessible header layout used across detail
 * pages (samples, boxes, experiments, studies) and expose a simple API for
 * adding action buttons or controls.
 */

import type * as React from "react";
import { cn } from "@/lib/utils";

// Omit the HTML attribute `title` (string) since we accept a `title` ReactNode
export interface DetailHeaderProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "title"> {
  /** Small uppercase category label (e.g. "Sample", "Box") */
  category?: React.ReactNode;
  /** Primary title (required) */
  title: React.ReactNode;
  /** Optional subtitle shown below the title */
  subtitle?: React.ReactNode;
  /** Optional actions rendered on the right side (buttons, menus) */
  actions?: React.ReactNode;
}

/**
 * DetailHeader
 *
 * Minimal, composable header used on object detail pages.
 */
export function DetailHeader({
  category,
  title,
  subtitle,
  actions,
  className,
  ...props
}: DetailHeaderProps) {
  return (
    <div className={cn("flex flex-wrap items-center justify-between gap-4", className)} {...props}>
      <div>
        {category && (
          <p className="text-xs uppercase tracking-wide text-muted-foreground">{category}</p>
        )}

        <h1 className="text-2xl font-semibold">{title}</h1>

        {subtitle && <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>}
      </div>

      <div className="flex flex-wrap gap-2">{actions}</div>
    </div>
  );
}

export default DetailHeader;
