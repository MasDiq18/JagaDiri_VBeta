"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { 
  Home, 
  Clock, 
  MessageSquare, 
  Heart, 
  Calendar, 
  Users, 
  User, 
  LogOut, 
  Menu, 
  X,
  Bell,
  ShieldAlert
} from "lucide-react";
import { Logo } from "@/components/shared/logo";
import { SOSButton } from "@/components/dashboard/sos-button";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { apiService } from "@/lib/api";

const SIDEBAR_ITEMS = [
  { label: "Dashboard", href: "/dashboard", icon: Home },
  { label: "SafePing Harian", href: "/dashboard/safeping", icon: Clock },
  { label: "Konsultasi Dokter", href: "/dashboard/consultation", icon: MessageSquare },
  { label: "Rekam Medis & MedCard", href: "/dashboard/health", icon: Heart },
  { label: "Jadwal Obat (Reminder)", href: "/dashboard/medication", icon: Calendar },
  { label: "Portal Keluarga", href: "/dashboard/family", icon: Users },
  { label: "Profil Saya", href: "/dashboard/profile", icon: User },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Auth Guard
    if (typeof window !== "undefined") {
      const user = apiService.getCurrentUser();
      const token = localStorage.getItem("jagadiri_access_token");
      if (!token || !user) {
        router.push("/login");
      } else {
        setCurrentUser(user);
      }
      setLoading(false);

      // Restore Senior Mode dari localStorage
      const savedSenior = localStorage.getItem("jd_senior_mode");
      if (savedSenior === "true") {
        document.documentElement.dataset.seniorMode = "true";
      }
    }
  }, [router]);

  const handleLogout = () => {
    apiService.logout();
    router.push("/login");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-text-secondary font-medium">Memuat dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col md:flex-row relative">
      {/* Mobile Navbar Header */}
      <header className="md:hidden w-full h-16 bg-surface border-b border-gray-100 flex items-center justify-between px-6 z-40 sticky top-0">
        <Logo size="sm" />
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-xl bg-gray-50 hover:bg-gray-100 text-text-primary"
        >
          {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </header>

      {/* Left Sidebar (Desktop & Drawer Mobile) */}
      <aside 
        className={`fixed md:sticky top-0 left-0 h-screen w-72 bg-surface border-r border-gray-100 flex flex-col z-50 transition-transform duration-300 md:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Sidebar Header */}
        <div className="h-20 flex items-center justify-between px-8 border-b border-gray-100">
          <Logo />
          <button 
            onClick={() => setSidebarOpen(false)}
            className="md:hidden p-1.5 rounded-lg bg-gray-50 text-text-primary"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Sidebar Menu Items */}
        <nav className="flex-1 py-6 px-4 space-y-1 overflow-y-auto">
          {SIDEBAR_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link 
                key={item.href} 
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold transition-all duration-200 ${
                  isActive 
                    ? "bg-primary text-white shadow-glow" 
                    : "text-text-secondary hover:bg-primary-light hover:text-primary"
                }`}
              >
                <Icon className="w-5 h-5 shrink-0" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Sidebar Footer User Card */}
        <div className="p-6 border-t border-gray-100 space-y-4">
          {currentUser && (
            <div className="flex items-center gap-3">
              <Avatar size="md" />
              <div className="overflow-hidden">
                <p className="font-bold text-text-primary truncate">{currentUser.full_name}</p>
                <Badge variant={currentUser.subscription_tier === "gold" ? "warning" : "default"}>
                  {currentUser.subscription_tier === "gold" ? "👑 Premium" : "⭐ Basic"}
                </Badge>
              </div>
            </div>
          )}
          <button 
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2.5 px-4 py-3 rounded-xl bg-danger-light hover:bg-danger text-danger hover:text-white font-semibold transition-colors duration-200"
          >
            <LogOut className="w-5 h-5" />
            <span>Keluar</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Desktop Top Header */}
        <header className="hidden md:flex w-full h-20 bg-surface border-b border-gray-100 items-center justify-between px-10 sticky top-0 z-30">
          <div>
            <h2 className="text-heading-lg font-bold text-text-primary">
              Halo, {currentUser?.full_name?.split(" ")[0]}!
            </h2>
            <p className="text-xs text-text-secondary">Selalu jaga kondisi Anda hari ini.</p>
          </div>
          <div className="flex items-center gap-6">
            {/* Notification Badge */}
            <button className="relative p-2.5 rounded-xl bg-gray-50 hover:bg-gray-100 text-text-secondary transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-danger animate-pulse" />
            </button>
            <div className="flex items-center gap-3 border-l border-gray-100 pl-6">
              <Avatar size="md" />
              <div>
                <p className="text-body-sm font-bold text-text-primary">{currentUser?.full_name}</p>
                <p className="text-xs text-text-secondary truncate max-w-[120px]">{currentUser?.email}</p>
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Pages Mount */}
        <main className="flex-1 p-6 md:p-10 max-w-6xl w-full mx-auto space-y-8 pb-24 md:pb-10">
          {children}
        </main>
      </div>

      {/* Persistent SOS Floating Action Button */}
      <SOSButton />
    </div>
  );
}
