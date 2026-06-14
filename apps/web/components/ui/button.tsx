"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 font-semibold rounded-xl transition-all duration-300 active:scale-[0.97] disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px] min-w-[44px] focus:outline-none focus:ring-2 focus:ring-offset-2",
  {
    variants: {
      variant: {
        primary:
          "bg-primary text-white hover:bg-primary-dark hover:shadow-glow focus:ring-primary/30",
        secondary:
          "bg-secondary text-white hover:bg-secondary-dark hover:shadow-glow-secondary focus:ring-secondary/30",
        danger:
          "bg-danger text-white font-bold hover:bg-danger-dark focus:ring-danger/30",
        outline:
          "border-2 border-primary text-primary hover:bg-primary hover:text-white focus:ring-primary/30",
        ghost:
          "text-primary hover:bg-primary-light focus:ring-primary/30",
        "outline-white":
          "border-2 border-white text-white hover:bg-white hover:text-primary focus:ring-white/30",
        white:
          "bg-white text-primary hover:bg-gray-50 focus:ring-white/30",
      },
      size: {
        sm: "px-4 py-2 text-sm",
        md: "px-6 py-3 text-base",
        lg: "px-8 py-4 text-lg",
        xl: "px-10 py-5 text-xl",
        icon: "p-3",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, isLoading, children, disabled, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && <Loader2 className="w-5 h-5 animate-spin" />}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
