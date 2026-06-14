"use client";

import { useState, useEffect } from "react";
import { 
  Heart, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  MessageSquare, 
  ArrowRight,
  TrendingUp,
  Brain,
  Plus,
  Database,
  Wifi,
  WifiOff
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { apiService } from "@/lib/api";
import Link from "next/link";

export default function DashboardHome() {
  const [loading, setLoading] = useState(true);
  
  // SafePing State
  const [pingConfig, setPingConfig] = useState<any>(null);
  const [checkedInToday, setCheckedInToday] = useState(false);
  const [mood, setMood] = useState<number | null>(null);
  const [note, setNote] = useState("");
  const [showCheckInForm, setShowCheckInForm] = useState(false);
  
  // Med Reminders State
  const [medReminders, setMedReminders] = useState<any[]>([]);
  const [takenMeds, setTakenMeds] = useState<string[]>([]);
  
  // Vitals State
  const [vitals, setVitals] = useState<any[]>([]);
  
  // AI Insight State
  const [insight, setInsight] = useState<any>(null);

  // Backend / DB connection status
  const [backendStatus, setBackendStatus] = useState<{
    api: boolean; database: string; latency_ms: number | null; checked: boolean;
  }>({ api: false, database: "...", latency_ms: null, checked: false });

  // Inline error states (ganti alert())
  const [checkInError, setCheckInError] = useState("");
  const [medError, setMedError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const config = await apiService.getSafePingConfig();
        setPingConfig(config);
        
        const meds = await apiService.getReminders();
        setMedReminders(meds);
        
        const vt = await apiService.getVitals();
        setVitals(vt);
        
        const ins = await apiService.getHealthInsights();
        setInsight(ins);
      } catch (err) {
        console.error("Gagal memuat data dashboard:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();

    // Cek status koneksi backend & database
    apiService.checkBackendStatus().then(status => {
      setBackendStatus({ ...status, checked: true });
    });
  }, []);

  const handleCheckInSubmit = async () => {
    if (mood === null) return;
    setCheckInError("");
    try {
      await apiService.checkIn(mood, note);
      setCheckedInToday(true);
      setShowCheckInForm(false);
      const ins = await apiService.getHealthInsights();
      setInsight(ins);
    } catch (err) {
      setCheckInError("Gagal mengirim check-in. Silakan coba lagi.");
    }
  };

  const handleMedTake = async (medId: string) => {
    setMedError("");
    try {
      await apiService.markMedTaken(medId, "Diminum tepat waktu");
      setTakenMeds(prev => [...prev, medId]);
    } catch (err) {
      setMedError("Gagal mencatat obat diminum. Silakan coba lagi.");
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

      {/* Status Bar Koneksi Server & Database */}
      <div className={`px-4 py-3 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs font-medium transition-colors ${
        !backendStatus.checked
          ? "bg-gray-50 border-gray-200 text-text-secondary"
          : backendStatus.api && backendStatus.database === "connected"
          ? "bg-success-light border-success/30 text-success"
          : backendStatus.api
          ? "bg-warning-light border-warning/30 text-warning-dark"
          : "bg-gray-100 border-gray-300 text-text-secondary"
      }`}>
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-1.5">
            {backendStatus.api
              ? <Wifi className="w-3.5 h-3.5 shrink-0" />
              : <WifiOff className="w-3.5 h-3.5 shrink-0" />}
            <span className="font-bold">API:</span>
            <span>
              {!backendStatus.checked
                ? "Memeriksa..."
                : backendStatus.api
                ? `Terhubung${backendStatus.latency_ms ? ` (${backendStatus.latency_ms}ms)` : ""}`
                : "Tidak Terhubung — Mode Offline"}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 shrink-0" />
            <span className="font-bold">Database:</span>
            <span className="capitalize">
              {!backendStatus.checked ? "Memeriksa..." : backendStatus.database}
            </span>
          </div>
        </div>
        {!backendStatus.api && backendStatus.checked && (
          <span className="text-text-secondary">
            💡 Jalankan: <code className="bg-gray-200 px-1 py-0.5 rounded text-[10px]">docker compose up</code> di folder proyek
          </span>
        )}
      </div>

      {/* Top Banner Alert if not checked-in */}
      {!checkedInToday && (
        <div className="p-5 rounded-2xl bg-warning-light border border-warning/30 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex gap-3 items-start">
            <AlertCircle className="w-6 h-6 text-warning-dark shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-text-primary">Perhatian: Check-in SafePing Hari Ini Belum Dilakukan</p>
              <p className="text-body-sm text-text-secondary">SafePing terjadwal Anda pukul {pingConfig?.check_in_time || "08:00"}. Harap segera check-in agar kontak darurat tidak khawatir.</p>
            </div>
          </div>
          <Button onClick={() => setShowCheckInForm(true)} size="sm">
            Check-In Sekarang
          </Button>
        </div>
      )}

      {/* Main Grid widgets */}
      <div className="grid md:grid-cols-3 gap-8">
        
        {/* SafePing Checkin Widget */}
        <Card className="space-y-4 md:col-span-2">
          <div className="flex justify-between items-center border-b border-gray-100 pb-4">
            <div className="flex items-center gap-2.5">
              <Clock className="w-5 h-5 text-primary" />
              <h3 className="font-heading font-bold text-heading-md">SafePing Status Harian</h3>
            </div>
            <Badge variant={checkedInToday ? "success" : "warning"}>
              {checkedInToday ? "Terproteksi" : "Perlu Check-In"}
            </Badge>
          </div>

          {checkedInToday ? (
            <div className="text-center py-8 space-y-4">
              <div className="w-16 h-16 rounded-full bg-success-light mx-auto flex items-center justify-center">
                <CheckCircle className="w-10 h-10 text-success" />
              </div>
              <div>
                <p className="font-bold text-text-primary text-heading-md">Check-in Selesai!</p>
                <p className="text-text-secondary text-body-sm mt-1">Sistem mencatat kondisi Anda baik. Terima kasih telah melakukan pembaruan keselamatan.</p>
              </div>
            </div>
          ) : (
            <div className="py-4 space-y-6">
              {!showCheckInForm ? (
                <div className="text-center space-y-4">
                  <p className="text-text-secondary text-body-sm">Kirim kabar keselamatan Anda dengan sekali klik.</p>
                  <Button onClick={() => setShowCheckInForm(true)} className="w-full">
                    Kirim Laporan Keselamatan (Check-In)
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-body-sm font-semibold text-text-primary">Bagaimana perasaan/kondisi Anda saat ini?</p>
                  <div className="flex justify-around gap-2">
                    {[
                      { val: 1, label: "🤒 Sakit" },
                      { val: 2, label: "😟 Lemas" },
                      { val: 3, label: "😐 Biasa" },
                      { val: 4, label: "🙂 Baik" },
                      { val: 5, label: "😊 Segar" }
                    ].map(item => (
                      <button
                        key={item.val}
                        onClick={() => setMood(item.val)}
                        className={`flex flex-col items-center justify-center p-3 rounded-xl border-2 transition-all flex-1 ${
                          mood === item.val 
                            ? "border-primary bg-primary-light text-primary font-bold" 
                            : "border-gray-100 hover:border-gray-200"
                        }`}
                      >
                        <span className="text-lg">{item.label.split(" ")[0]}</span>
                        <span className="text-[10px] mt-1">{item.label.split(" ")[1]}</span>
                      </button>
                    ))}
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-text-primary mb-1.5">Catatan singkat (Opsional)</label>
                    <input 
                      type="text" 
                      placeholder="Contoh: Sedikit flu tapi sudah minum obat."
                      className="input-field text-body-sm"
                      value={note}
                      onChange={(e) => setNote(e.target.value)}
                    />
                  </div>

                  {checkInError && (
                    <div className="p-3 rounded-xl bg-danger-light border border-danger/30 text-danger text-xs flex gap-1.5 items-center">
                      <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                      {checkInError}
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button variant="ghost" onClick={() => { setShowCheckInForm(false); setCheckInError(""); }} className="flex-1">
                      Batal
                    </Button>
                    <Button onClick={handleCheckInSubmit} className="flex-1" disabled={mood === null}>
                      Kirim Laporan
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </Card>

        {/* AI Health Insights */}
        <Card className="space-y-4 bg-gradient-to-br from-primary-50 to-secondary-50 border border-primary-200">
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-primary" />
            <h3 className="font-heading font-bold text-heading-md">Asisten AI JagaDiri</h3>
          </div>

          {insight && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-white/75 border border-primary-100">
                <p className="text-body-sm font-bold text-text-primary">Skor Kesehatan Anda</p>
                <div className="flex items-end gap-2 mt-1">
                  <span className="text-heading-2xl font-extrabold text-primary leading-none">{insight.skor_kesehatan}</span>
                  <span className="text-text-secondary text-xs pb-1">/100</span>
                </div>
              </div>

              <div className="space-y-2 text-body-sm text-text-primary">
                <p className="font-bold text-xs text-text-secondary uppercase tracking-wider">Ringkasan Kesehatan</p>
                <p className="text-xs">{insight.ringkasan_kesehatan}</p>
              </div>

              <div className="space-y-2">
                <p className="font-bold text-xs text-text-secondary uppercase tracking-wider">Saran & Pengingat</p>
                <ul className="space-y-1.5 text-xs text-text-primary">
                  {insight.saran_kesehatan.map((s: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-primary mt-0.5">•</span>
                      <span>{s}</span>
                    </li>
                  ))}
                  {insight.pengingat.map((p: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-1.5 text-secondary font-semibold">
                      <span className="text-secondary mt-0.5">•</span>
                      <span>{p}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </Card>
      </div>

      {/* Medications & Vitals */}
      <div className="grid md:grid-cols-2 gap-8">
        
        {/* Medication checklist */}
        <Card className="space-y-4">
          <div className="flex justify-between items-center border-b border-gray-100 pb-4">
            <div className="flex items-center gap-2.5">
              <CheckCircle className="w-5 h-5 text-secondary" />
              <h3 className="font-heading font-bold text-heading-md">Jadwal Obat Hari Ini</h3>
            </div>
            <Link href="/dashboard/medication">
              <Button variant="ghost" size="sm" className="text-xs p-0 h-auto font-bold flex items-center">
                Semua Obat <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Button>
            </Link>
          </div>

          <div className="space-y-3">
            {medError && (
              <div className="p-3 rounded-xl bg-danger-light border border-danger/30 text-danger text-xs flex gap-1.5 items-center">
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                {medError}
              </div>
            )}
            {medReminders.length > 0 ? (
              medReminders.map((med) => {
                const isTaken = takenMeds.includes(med.id);
                return (
                  <div key={med.id} className="p-4 rounded-xl border border-gray-100 flex items-center justify-between gap-4 bg-surface hover:bg-gray-50/50 transition-colors">
                    <div>
                      <p className="font-bold text-text-primary">{med.medication_name}</p>
                      <p className="text-xs text-text-secondary mt-0.5">Dosis: {med.dosage || "1 pcs"} • Jam: {med.reminder_times?.join(", ") || "08:00"}</p>
                    </div>
                    {isTaken ? (
                      <Badge variant="success">Sudah Diminum</Badge>
                    ) : (
                      <Button onClick={() => handleMedTake(med.id)} size="sm" variant="outline" className="border-secondary text-secondary hover:bg-secondary hover:text-white">
                        Konfirmasi Minum
                      </Button>
                    )}
                  </div>
                );
              })
            ) : (
              <div className="text-center py-6">
                <p className="text-text-secondary text-body-sm">Tidak ada jadwal minum obat aktif.</p>
                <Link href="/dashboard/medication">
                  <Button variant="outline" size="sm" className="mt-3">
                    Tambah Pengingat Obat <Plus className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </Card>

        {/* Vital Signs Summary */}
        <Card className="space-y-4">
          <div className="flex justify-between items-center border-b border-gray-100 pb-4">
            <div className="flex items-center gap-2.5">
              <TrendingUp className="w-5 h-5 text-primary" />
              <h3 className="font-heading font-bold text-heading-md">Tanda Vital Terakhir</h3>
            </div>
            <Link href="/dashboard/health">
              <Button variant="ghost" size="sm" className="text-xs p-0 h-auto font-bold flex items-center">
                Buka Log Medis <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Button>
            </Link>
          </div>

          <div className="grid grid-cols-3 gap-4">
            {vitals.map((v) => {
              const label = v.metric_type === "blood_pressure" ? "Tensi" : v.metric_type === "heart_rate" ? "Jantung" : "Suhu";
              const value = v.metric_type === "blood_pressure" ? `${v.value_systolic}/${v.value_diastolic}` : v.value_numeric;
              return (
                <div key={v.id} className="p-4 rounded-xl border border-gray-100 text-center space-y-1 bg-surface">
                  <p className="text-xs text-text-secondary font-bold uppercase tracking-wider">{label}</p>
                  <p className="text-heading-md font-extrabold text-text-primary">{value}</p>
                  <p className="text-[10px] text-text-secondary">{v.unit}</p>
                </div>
              );
            })}
          </div>

          <div className="p-4 rounded-xl bg-primary-light/30 border border-primary/10 flex items-center justify-between gap-4">
            <div className="flex gap-2.5 items-start">
              <Heart className="w-5 h-5 text-primary shrink-0 mt-0.5" />
              <p className="text-xs text-text-primary leading-relaxed">Gunakan fitur <strong>MedCard QR code</strong> jika Anda bepergian jauh sendirian untuk keselamatan penyelamatan tak terduga.</p>
            </div>
          </div>
        </Card>

      </div>
    </div>
  );
}
