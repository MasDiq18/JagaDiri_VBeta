import * as React from "react";
import { cn } from "@/lib/utils";
import { type LucideIcon } from "lucide-react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: LucideIcon;
  iconPosition?: "left" | "right";
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, error, icon: Icon, iconPosition = "left", id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-text-primary mb-2"
          >
            {label}
          </label>
        )}
        <div className="relative">
          {Icon && iconPosition === "left" && (
            <Icon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-secondary" />
          )}
          <input
            type={type}
            id={inputId}
            className={cn(
              "input-field",
              Icon && iconPosition === "left" && "pl-12",
              Icon && iconPosition === "right" && "pr-12",
              error && "border-danger focus:ring-danger/30 focus:border-danger",
              className
            )}
            ref={ref}
            {...props}
          />
          {Icon && iconPosition === "right" && (
            <Icon className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-secondary" />
          )}
        </div>
        {error && (
          <p className="mt-1.5 text-sm text-danger flex items-center gap-1">
            <span className="w-1 h-1 rounded-full bg-danger" />
            {error}
          </p>
        )}
      </div>
    );
  }
);
Input.displayName = "Input";

export { Input };
