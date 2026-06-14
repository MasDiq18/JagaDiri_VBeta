import { cn } from "@/lib/utils";
import { cva, type VariantProps } from "class-variance-authority";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full font-medium text-xs px-3 py-1",
  {
    variants: {
      variant: {
        default: "bg-primary-light text-primary",
        primary: "bg-primary text-white",
        secondary: "bg-secondary-light text-secondary",
        success: "bg-success-light text-success",
        warning: "bg-warning-light text-warning-dark",
        danger: "bg-danger-light text-danger",
        outline: "border border-gray-300 text-text-secondary bg-transparent",
        active: "bg-success-light text-success",
        pending: "bg-warning-light text-warning-dark",
        urgent: "bg-danger text-white",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  dot?: boolean;
}

export function Badge({ className, variant, dot, children, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props}>
      {dot && (
        <span
          className={cn(
            "w-1.5 h-1.5 rounded-full",
            variant === "success" || variant === "active" ? "bg-success" : "",
            variant === "warning" || variant === "pending" ? "bg-warning" : "",
            variant === "danger" || variant === "urgent" ? "bg-danger" : "",
            variant === "default" ? "bg-primary" : "",
            variant === "secondary" ? "bg-secondary" : ""
          )}
        />
      )}
      {children}
    </span>
  );
}
