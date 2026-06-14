"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Home, Calendar, LogOut, Heart, User, Clock } from "lucide-react";
import { Logo } from "@/components/shared/logo";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { apiService } from "@/lib/api";

export default function DoctorLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [currentDoctor, setCurrentDoctor] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const user = apiService.getCurrentUser();
      const token = localStorage.getItem("jagadiri_access_token");
      // For demo purposes, we allow any logged-in user to view the doctor portal,
      // but in production, we check if they are a doctor
      if (!token || !user) {
        router.push("/login");
      } else {
        setCurrentDoctor(user);
      }
      setLoading(false);
    }
  }, [router]);

  const handleLogout = () => {
    apiService.logout();
    router.push("/login");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col md:flex-row relative">
      
      {/* Sidebar */}
      <aside className="w-full md:w-72 bg-surface border-b md:border-b-0 md:border-r border-gray-100 flex flex-col z-50">
        <div className="h-20 flex items-center px-8 border-b border-gray-100">
          <Logo />
          <Badge variant="secondary" className="ml-2">Portal Dokter</Badge>
        </div>

        <nav className="flex-1 py-6 px-4 space-y-1">
          <Link 
            href="/doctor"
            className="flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-text-secondary hover:bg-primary-light hover:text-primary transition-all duration-200"
          >
            <Home className="w-5 h-5" />
            <span>Dashboard Dokter</span>
          </Link>
          
          <Link 
            href="/doctor/schedule"
            className="flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-text-secondary hover:bg-primary-light hover:text-primary transition-all duration-200"
          >
            <Calendar className="w-5 h-5" />
            <span>Jadwal Praktik</span>
          </Link>
        </nav>

        <div className="p-6 border-t border-gray-100 space-y-4">
          <div className="flex items-center gap-3">
            <Avatar size="md" online={true} />
            <div>
              <p className="font-bold text-text-primary text-body-sm truncate">{currentDoctor?.full_name || "dr. Rian Pratama"}</p>
              <p className="text-xs text-text-secondary">Dokter Umum</p>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2.5 px-4 py-3 rounded-xl bg-danger-light hover:bg-danger text-danger hover:text-white font-semibold transition-all duration-200"
          >
            <LogOut className="w-5 h-5" />
            <span>Keluar Portal</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="hidden md:flex w-full h-20 bg-surface border-b border-gray-100 items-center justify-between px-10">
          <div>
            <h2 className="text-heading-lg font-bold text-text-primary">Portal Layanan Medis JagaDiri</h2>
            <p className="text-xs text-text-secondary">Kelola rekam medis pasien dan SOAP secara aman.</p>
          </div>
        </header>

        <main className="flex-1 p-6 md:p-10 max-w-6xl w-full mx-auto space-y-8">
          {children}
        </main>
      </div>
    </div>
  );
}
