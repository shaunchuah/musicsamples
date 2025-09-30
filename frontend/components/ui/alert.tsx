import { cva, type VariantProps } from "class-variance-authority";
import { AlertTriangle, CheckCircle, Info, XCircle } from "lucide-react";
import type * as React from "react";
import { cn } from "@/lib/utils";

const alertVariants = cva(
  "relative w-full rounded-lg border px-4 py-3 text-sm grid has-[>svg]:grid-cols-[calc(var(--spacing)*4)_1fr] grid-cols-[0_1fr] has-[>svg]:gap-x-3 gap-y-0.5 items-start [&>svg]:size-4 [&>svg]:translate-y-0.5 [&>svg]:text-current",
  {
    variants: {
      variant: {
        default: "bg-card text-card-foreground",
        destructive:
          "text-destructive bg-card [&>svg]:text-current *:data-[slot=alert-description]:text-destructive/90",
        error:
          "bg-card text-red-700 bg-red-50 border border-red-400 [&>svg]:text-red-700",
        success:
          "bg-card text-green-700 bg-green-50 border border-green-400 [&>svg]:text-green-700",
        warning:
          "bg-card text-yellow-700 bg-yellow-50 border border-yellow-400 [&>svg]:text-yellow-700",
        info: "bg-card text-blue-700 bg-blue-50 border border-blue-400 [&>svg]:text-blue-700",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

function Alert({
  className,
  variant,
  ...props
}: React.ComponentProps<"div"> & VariantProps<typeof alertVariants>) {
  return (
    <div
      data-slot="alert"
      role="alert"
      className={cn(alertVariants({ variant }), className)}
      {...props}
    />
  );
}

function AlertTitle({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="alert-title"
      className={cn("col-start-2 line-clamp-1 min-h-4 font-medium tracking-tight", className)}
      {...props}
    />
  );
}

function AlertDescription({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="alert-description"
      className={cn(
        "col-start-2 grid justify-items-start gap-1 text-sm [&_p]:leading-relaxed",
        className,
      )}
      {...props}
    />
  );
}

function AlertSuccess({ className, children, ...props }: React.ComponentProps<"div">) {
  return (
    <Alert variant="success" className={className} {...props}>
      <CheckCircle />
      {children}
    </Alert>
  );
}

function AlertWarning({ className, children, ...props }: React.ComponentProps<"div">) {
  return (
    <Alert variant="warning" className={className} {...props}>
      <AlertTriangle />
      {children}
    </Alert>
  );
}

function AlertError({ className, children, ...props }: React.ComponentProps<"div">) {
  return (
    <Alert variant="error" className={className} {...props}>
      <XCircle />
      {children}
    </Alert>
  );
}

function AlertInfo({ className, children, ...props }: React.ComponentProps<"div">) {
  return (
    <Alert variant="info" className={className} {...props}>
      <Info />
      {children}
    </Alert>
  );
}

export { Alert, AlertTitle, AlertDescription, AlertSuccess, AlertWarning, AlertError, AlertInfo };
