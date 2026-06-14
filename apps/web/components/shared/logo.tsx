import { Shield } from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";

interface LogoProps {
  variant?: "dark" | "light" | "gradient";
  size?: "sm" | "md" | "lg";
  showText?: boolean;
  className?: string;
}

export function Logo({ variant = "dark", size = "md", showText = true, className }: LogoProps) {
  const sizes = {
    sm: { icon: "w-6 h-6", text: "text-lg" },
    md: { icon: "w-8 h-8", text: "text-xl" },
    lg: { icon: "w-10 h-10", text: "text-2xl" },
  };

  const colors = {
    dark: { icon: "text-primary", text: "text-text-primary" },
    light: { icon: "text-white", text: "text-white" },
    gradient: { icon: "text-primary", text: "gradient-text" },
  };

  return (
    <Link href="/" className={cn("flex items-center gap-2.5 group", className)}>
      <div className="relative">
        <Shield
          className={cn(
            sizes[size].icon,
            colors[variant].icon,
            "transition-transform duration-300 group-hover:scale-110"
          )}
          strokeWidth={2.5}
        />
        <div
          className={cn(
            "absolute inset-0 rounded-full blur-lg opacity-0 group-hover:opacity-30 transition-opacity duration-300",
            variant === "light" ? "bg-white" : "bg-primary"
          )}
        />
      </div>
      {showText && (
        <span
          className={cn(
            "font-heading font-extrabold tracking-tight",
            sizes[size].text,
            colors[variant].text
          )}
        >
          Jaga<span className={variant === "light" ? "text-white/80" : "text-primary"}>Diri</span>
        </span>
      )}
    </Link>
  );
}
