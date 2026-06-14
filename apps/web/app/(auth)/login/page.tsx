"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Mail, Lock, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiService } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      await apiService.login(email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        "Terjadi kesalahan saat masuk. Periksa kembali email dan kata sandi Anda."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-heading-lg font-bold text-text-primary">Selamat Datang</h2>
        <p className="text-text-secondary text-body-sm mt-1">Masuk untuk mengakses dashboard JagaDiri Anda</p>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-danger-light border border-danger/30 text-danger text-body-sm flex items-start gap-2.5">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Alamat Email"
          type="email"
          placeholder="nama@email.com"
          icon={Mail}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={isLoading}
        />

        <Input
          label="Kata Sandi"
          type="password"
          placeholder="••••••••"
          icon={Lock}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          disabled={isLoading}
        />

        <div className="flex justify-end">
          <Link href="/forgot-password" className="text-xs font-semibold text-primary hover:underline">
            Lupa Kata Sandi?
          </Link>
        </div>

        <Button type="submit" className="w-full" isLoading={isLoading}>
          Masuk Sekarang
        </Button>
      </form>

      <div className="text-center pt-2 text-body-sm text-text-secondary">
        Belum memiliki akun?{" "}
        <Link href="/register" className="font-semibold text-primary hover:underline">
          Daftar Gratis
        </Link>
      </div>
    </div>
  );
}
