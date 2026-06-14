import type { ReactNode } from "react";
import { Logo } from "@/components/shared/logo";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-900 to-secondary-900 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background gradients */}
      <div className="absolute top-[-20%] left-[-20%] w-[60%] h-[60%] rounded-full bg-primary-500/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-20%] w-[60%] h-[60%] rounded-full bg-secondary-500/10 blur-[120px] pointer-events-none" />
      
      <div className="w-full max-w-md bg-white/90 dark:bg-surface/90 backdrop-blur-xl p-8 rounded-2xl shadow-glass border border-white/20 dark:border-white/5 space-y-6 relative z-10">
        <div className="flex justify-center">
          <Logo variant="dark" size="lg" />
        </div>
        {children}
      </div>
    </div>
  );
}
