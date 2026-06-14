"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { User, Mail, Phone, Lock, Heart, Shield, Bell, AlertCircle, ArrowLeft, ArrowRight, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiService } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // Step 1 Form Data
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");

  // Step 2 Form Data
  const [bloodType, setBloodType] = useState("O+");
  const [allergies, setAllergies] = useState("");
  const [conditions, setConditions] = useState("");

  // Step 3 Form Data
  const [contactName, setContactName] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [contactRelation, setContactRelation] = useState("");

  // Step 4 Form Data
  const [checkInTime, setCheckInTime] = useState("08:00");
  const [windowMin, setWindowMin] = useState(120);

  const handleNext = (e: React.FormEvent) => {
    e.preventDefault();
    if (step < 4) {
      setStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(prev => prev - 1);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      // 1. Registrasi akun
      await apiService.register({
        email,
        password,
        full_name: fullName,
        phone,
      });

      // 2. Login otomatis untuk mendapatkan session
      await apiService.login(email, password);

      // 3. Simpan profil medis (data dari Step 2)
      if (bloodType || allergies || conditions) {
        await apiService.updateMedProfile({
          blood_type: bloodType || null,
          allergies: allergies ? allergies.split(",").map((s: string) => s.trim()).filter(Boolean) : [],
          chronic_conditions: conditions ? conditions.split(",").map((s: string) => s.trim()).filter(Boolean) : [],
        });
      }

      // 4. Simpan kontak darurat (data dari Step 3)
      if (contactName && contactPhone) {
        await apiService.addEmergencyContact({
          name: contactName,
          phone: contactPhone,
          relation: contactRelation || "Keluarga",
          priority: 1,
        });
      }

      // 5. Simpan konfigurasi SafePing (data dari Step 4)
      await apiService.updateSafePingConfig({
        is_enabled: true,
        check_in_time: checkInTime,
        response_window_minutes: windowMin,
        escalation_to_emergency_contacts: true,
      });

      router.push("/dashboard");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        "Gagal melakukan registrasi. Pastikan kata sandi mengandung huruf besar, kecil, dan angka."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Progress Bar */}
      <div className="flex items-center justify-between mb-2">
        {[1, 2, 3, 4].map((num) => (
          <div key={num} className="flex items-center flex-1 last:flex-none">
            <div 
              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all duration-300 ${
                step >= num 
                  ? "bg-primary text-white" 
                  : "bg-gray-100 text-text-secondary border border-gray-200"
              }`}
            >
              {step > num ? <Check className="w-4 h-4" /> : num}
            </div>
            {num < 4 && (
              <div 
                className={`h-[3px] flex-1 mx-2 transition-all duration-300 ${
                  step > num ? "bg-primary" : "bg-gray-200"
                }`}
              />
            )}
          </div>
        ))}
      </div>

      <div className="text-center">
        <h2 className="text-heading-lg font-bold text-text-primary">
          {step === 1 && "Detail Akun"}
          {step === 2 && "Informasi Medis"}
          {step === 3 && "Kontak Darurat"}
          {step === 4 && "Proteksi SafePing"}
        </h2>
        <p className="text-text-secondary text-body-sm mt-1">
          {step === 1 && "Lengkapi data dasar untuk membuat akun Anda"}
          {step === 2 && "Data penting untuk penolong jika keadaan darurat"}
          {step === 3 && "Keluarga/teman terdekat yang akan dihubungi jika Anda sakit"}
          {step === 4 && "Atur waktu check-in harian keselamatan Anda"}
        </p>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-danger-light border border-danger/30 text-danger text-body-sm flex items-start gap-2.5">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Step 1: Account Info */}
      {step === 1 && (
        <form onSubmit={handleNext} className="space-y-4">
          <Input
            label="Nama Lengkap"
            placeholder="Budi Santoso"
            icon={User}
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
          <Input
            label="Alamat Email"
            type="email"
            placeholder="budi@email.com"
            icon={Mail}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            label="Nomor Telepon"
            placeholder="+6281234567890"
            icon={Phone}
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
          />
          <Input
            label="Kata Sandi"
            type="password"
            placeholder="Minimal 8 karakter"
            icon={Lock}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button type="submit" className="w-full">
            Lanjut <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </form>
      )}

      {/* Step 2: Medical Profile */}
      {step === 2 && (
        <form onSubmit={handleNext} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">Golongan Darah</label>
            <select
              className="input-field bg-white"
              value={bloodType}
              onChange={(e) => setBloodType(e.target.value)}
            >
              {["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          <Input
            label="Alergi Obat/Makanan (Opsional)"
            placeholder="Contoh: Debu, Parasetamol, Kacang"
            icon={Heart}
            value={allergies}
            onChange={(e) => setAllergies(e.target.value)}
          />
          <Input
            label="Riwayat Penyakit Kronis (Opsional)"
            placeholder="Contoh: Hipertensi, Asma, Maag"
            icon={Heart}
            value={conditions}
            onChange={(e) => setConditions(e.target.value)}
          />
          <div className="flex gap-3">
            <Button type="button" variant="outline" className="flex-1" onClick={handleBack}>
              <ArrowLeft className="w-4 h-4 mr-1" /> Kembali
            </Button>
            <Button type="submit" className="flex-1">
              Lanjut <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </form>
      )}

      {/* Step 3: Emergency Contacts */}
      {step === 3 && (
        <form onSubmit={handleNext} className="space-y-4">
          <Input
            label="Nama Kontak Darurat"
            placeholder="Rudi Santoso"
            icon={User}
            value={contactName}
            onChange={(e) => setContactName(e.target.value)}
            required
          />
          <Input
            label="Nomor Telepon Kontak"
            placeholder="+6281299998888"
            icon={Phone}
            value={contactPhone}
            onChange={(e) => setContactPhone(e.target.value)}
            required
          />
          <Input
            label="Hubungan Keluarga"
            placeholder="Contoh: Kakak, Orang Tua, Teman Kos"
            icon={Shield}
            value={contactRelation}
            onChange={(e) => setContactRelation(e.target.value)}
            required
          />
          <div className="flex gap-3">
            <Button type="button" variant="outline" className="flex-1" onClick={handleBack}>
              <ArrowLeft className="w-4 h-4 mr-1" /> Kembali
            </Button>
            <Button type="submit" className="flex-1">
              Lanjut <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </form>
      )}

      {/* Step 4: SafePing Setting */}
      {step === 4 && (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">Jam Check-In Harian</label>
            <input
              type="time"
              className="input-field"
              value={checkInTime}
              onChange={(e) => setCheckInTime(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">Batas Toleransi Respons (Menit)</label>
            <select
              className="input-field bg-white"
              value={windowMin}
              onChange={(e) => setWindowMin(Number(e.target.value))}
            >
              <option value={60}>60 menit (1 jam)</option>
              <option value={120}>120 menit (2 jam)</option>
              <option value={240}>240 menit (4 jam)</option>
              <option value={480}>480 menit (8 jam)</option>
            </select>
          </div>
          <div className="flex gap-3">
            <Button type="button" variant="outline" className="flex-1" onClick={handleBack} disabled={isLoading}>
              <ArrowLeft className="w-4 h-4 mr-1" /> Kembali
            </Button>
            <Button type="submit" className="flex-1" isLoading={isLoading}>
              Selesaikan <Check className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </form>
      )}

      <div className="text-center pt-2 text-body-sm text-text-secondary">
        Sudah terdaftar?{" "}
        <Link href="/login" className="font-semibold text-primary hover:underline">
          Masuk ke Akun
        </Link>
      </div>
    </div>
  );
}
