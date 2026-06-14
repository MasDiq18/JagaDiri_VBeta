"use client";

import { useState, useEffect } from "react";
import { User, Phone, Mail, Award, Eye, Save, Settings, Info, Heart } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { apiService } from "@/lib/api";

export default function ProfilePage() {
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);

  // Form states
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [nik, setNik] = useState("");
  
  // Settings States
  const [subscription, setSubscription] = useState("basic");
  const [seniorMode, setSeniorMode] = useState(false);

  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [saveError, setSaveError] = useState("");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const usr = apiService.getCurrentUser();
      setUser(usr);
      if (usr) {
        setFullName(usr.full_name);
        setPhone(usr.phone || "+62");
        setNik(usr.nik || "");
        setSubscription(usr.subscription_tier || "basic");
        
        // Read senior mode dari data attribute
        const hasSeniorMode = document.documentElement.dataset.seniorMode === "true";
        setSeniorMode(hasSeniorMode);

        // Restore senior mode from localStorage on mount
        const savedSenior = localStorage.getItem("jd_senior_mode");
        if (savedSenior === "true") {
          document.documentElement.dataset.seniorMode = "true";
          setSeniorMode(true);
        }
      }
      setLoading(false);
    }
  }, []);

  const handleToggleSeniorMode = (checked: boolean) => {
    setSeniorMode(checked);
    if (typeof window !== "undefined") {
      // Use data attribute to match CSS selector [data-senior-mode="true"]
      document.documentElement.dataset.seniorMode = checked ? "true" : "false";
      if (checked) {
        localStorage.setItem("jd_senior_mode", "true");
      } else {
        localStorage.removeItem("jd_senior_mode");
      }
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");

    try {
      // API or Mock updates
      const updatedUser = {
        ...user,
        full_name: fullName,
        phone,
        nik,
        subscription_tier: subscription
      };
      
      localStorage.setItem("jagadiri_user", JSON.stringify(updatedUser));
      setUser(updatedUser);
      setSaveError("");
      setMessage("Profil JagaDiri Anda berhasil diperbarui.");
      setTimeout(() => setMessage(""), 3000);
    } catch (err) {
      setSaveError("Gagal memperbarui profil. Silakan coba lagi.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h2 className="text-heading-xl font-bold text-text-primary">⚙️ Profil & Pengaturan Akun</h2>
        <p className="text-text-secondary text-body-sm mt-1">Kelola data pribadi Anda, pilih tier proteksi JagaDiri, dan atur mode kenyamanan visual.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        
        {/* Left Side: Profile Form */}
        <div className="md:col-span-2 space-y-6">
          <form onSubmit={handleSaveProfile}>
            <Card className="space-y-6">
              <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3">Informasi Pribadi</h3>
              
              {saveError && (
                <div className="p-3.5 rounded-xl bg-danger-light border border-danger/30 text-danger text-xs mb-3">
                  {saveError}
                </div>
              )}

              {message && (
                <div className="p-3.5 rounded-xl bg-success-light border border-success/30 text-success text-xs">
                  {message}
                </div>
              )}

              <div className="grid sm:grid-cols-2 gap-4">
                <Input
                  label="Nama Lengkap"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  icon={User}
                  required
                />
                
                <div className="relative">
                  <label className="block text-sm font-medium text-text-primary mb-2">Alamat Email</label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-secondary" />
                    <input
                      type="email"
                      className="input-field pl-12 bg-gray-50 text-text-secondary cursor-not-allowed"
                      value={user?.email || ""}
                      disabled
                    />
                  </div>
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                <Input
                  label="Nomor Telepon"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  icon={Phone}
                  required
                />

                <Input
                  label="Nomor Induk Kependudukan (NIK)"
                  placeholder="317xxxxxxxxxxxxx"
                  value={nik}
                  onChange={(e) => setNik(e.target.value)}
                  icon={Eye}
                  maxLength={16}
                />
              </div>

              {/* Subscriptions */}
              <div className="space-y-3 border-t border-gray-100 pt-6">
                <h4 className="font-heading font-bold text-body text-text-primary flex items-center gap-1.5">
                  <Award className="w-4 h-4 text-primary" />
                  Pilihan Paket Proteksi
                </h4>
                
                <div className="grid sm:grid-cols-3 gap-4">
                  {[
                    { id: "basic", label: "Basic Plan", desc: "Rp 0 / bln" },
                    { id: "standard", label: "Standard", desc: "Rp 29.000 / bln" },
                    { id: "gold", label: "Premium Gold", desc: "Rp 79.000 / bln" }
                  ].map(plan => (
                    <button
                      key={plan.id}
                      type="button"
                      onClick={() => setSubscription(plan.id)}
                      className={`p-4 rounded-xl border text-center transition-all ${
                        subscription === plan.id 
                          ? "border-primary bg-primary-light text-primary font-bold shadow-sm" 
                          : "border-gray-100 hover:border-gray-200"
                      }`}
                    >
                      <p className="text-body-sm font-bold">{plan.label}</p>
                      <p className="text-[10px] text-text-secondary mt-1">{plan.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <Button type="submit" isLoading={saving} className="w-full sm:w-auto px-8">
                  <Save className="w-4 h-4 mr-1.5" /> Simpan Perubahan
                </Button>
              </div>
            </Card>
          </form>
        </div>

        {/* Right Side: Accessibility & Options */}
        <div className="space-y-6">
          {/* Senior Mode Config card */}
          <Card className="space-y-4">
            <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3 flex items-center gap-1.5">
              <Settings className="w-5 h-5 text-primary" />
              Aksesibilitas
            </h3>

            <div className="flex justify-between items-start gap-4">
              <div>
                <p className="font-bold text-body-sm text-text-primary">Mode Lansia (Senior Mode)</p>
                <p className="text-xs text-text-secondary mt-0.5 leading-relaxed">
                  Perbesar seluruh tampilan tulisan dan tombol untuk mempermudah navigasi orang tua/lansia.
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer mt-1">
                <input
                  type="checkbox"
                  checked={seniorMode}
                  onChange={(e) => handleToggleSeniorMode(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
          </Card>

          {/* Privacy statement */}
          <Card className="bg-gradient-to-br from-primary-50 to-secondary-50 border border-primary-100 p-5 space-y-3">
            <h4 className="font-bold text-body-sm text-text-primary flex gap-1.5 items-center">
              <Heart className="w-4 h-4 text-primary" /> Privasi Data Dijamin
            </h4>
            <p className="text-xs text-text-primary leading-relaxed">
              JagaDiri tunduk sepenuhnya pada UU Perlindungan Data Pribadi (UU PDP). Rekam medis dan kontak darurat Anda tidak akan pernah disalahgunakan.
            </p>
          </Card>
        </div>

      </div>
    </div>
  );
}
