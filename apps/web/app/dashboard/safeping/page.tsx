"use client";

import { useState, useEffect } from "react";
import { Clock, Shield, Bell, Save, AlertTriangle, PlayCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { apiService } from "@/lib/api";

export default function SafePingPage() {
  const [loading, setLoading] = useState(true);
  const [config, setConfig] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  
  // Form values
  const [isEnabled, setIsEnabled] = useState(true);
  const [checkInTime, setCheckInTime] = useState("08:00");
  const [windowMin, setWindowMin] = useState(120);
  const [escalateContacts, setEscalateContacts] = useState(true);
  const [escalate119, setEscalate119] = useState(false);

  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [saveError, setSaveError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const cfg = await apiService.getSafePingConfig();
        setConfig(cfg);
        setIsEnabled(cfg.is_enabled);
        setCheckInTime(cfg.check_in_time);
        setWindowMin(cfg.response_window_minutes);
        setEscalateContacts(cfg.escalation_to_emergency_contacts);
        setEscalate119(cfg.escalation_to_119);

        const hist = await apiService.getCheckInHistory();
        setHistory(hist);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      const updated = await apiService.updateSafePingConfig({
        is_enabled: isEnabled,
        check_in_time: checkInTime,
        response_window_minutes: windowMin,
        escalation_to_emergency_contacts: escalateContacts,
        escalation_to_119: escalate119
      });
      setConfig(updated);
      setSaveError("");
      setMessage("Pengaturan SafePing berhasil disimpan.");
      setTimeout(() => setMessage(""), 3000);
    } catch (err) {
      setSaveError("Gagal memperbarui konfigurasi. Silakan coba lagi.");
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
        <h2 className="text-heading-xl font-bold text-text-primary">🛡️ Proteksi SafePing Harian</h2>
        <p className="text-text-secondary text-body-sm mt-1">SafePing adalah jaring pengaman kesehatan Anda yang mengecek kondisi Anda setiap hari secara proaktif.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        
        {/* Left Side: Configurations Form */}
        <div className="md:col-span-2 space-y-6">
          <form onSubmit={handleSave}>
            <Card className="space-y-6">
              <div className="flex justify-between items-center border-b border-gray-100 pb-4">
                <h3 className="font-heading font-bold text-heading-md text-text-primary">Pengaturan Proteksi</h3>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isEnabled}
                    onChange={(e) => setIsEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  <span className="ml-3 text-sm font-semibold text-text-primary">
                    {isEnabled ? "Aktif" : "Nonaktif"}
                  </span>
                </label>
              </div>

              {saveError && (
                <div className="p-3.5 rounded-xl bg-danger-light border border-danger/30 text-danger text-body-sm flex items-center gap-2">
                  <span>{saveError}</span>
                </div>
              )}

              {message && (
                <div className="p-3.5 rounded-xl bg-success-light border border-success/30 text-success text-body-sm flex items-center gap-2">
                  <Badge variant="success">Sukses</Badge>
                  <span>{message}</span>
                </div>
              )}

              <div className="grid sm:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Jam Check-In Harian
                  </label>
                  <input
                    type="time"
                    className="input-field"
                    value={checkInTime}
                    onChange={(e) => setCheckInTime(e.target.value)}
                    disabled={!isEnabled}
                    required
                  />
                  <p className="text-xs text-text-secondary mt-1.5">Waktu Anda mengirim konfirmasi keselamatan.</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Batas Toleransi Respons
                  </label>
                  <select
                    className="input-field bg-white"
                    value={windowMin}
                    onChange={(e) => setWindowMin(Number(e.target.value))}
                    disabled={!isEnabled}
                  >
                    <option value={30}>30 menit</option>
                    <option value={60}>60 menit (1 jam)</option>
                    <option value={120}>120 menit (2 jam)</option>
                    <option value={240}>240 menit (4 jam)</option>
                  </select>
                  <p className="text-xs text-text-secondary mt-1.5">Waktu tunggu sebelum sistem melakukan eskalasi darurat.</p>
                </div>
              </div>

              <div className="space-y-4 border-t border-gray-100 pt-6">
                <h4 className="font-heading font-bold text-body text-text-primary flex items-center gap-2">
                  <Bell className="w-4 h-4 text-primary" />
                  Rantai Eskalasi Darurat
                </h4>
                
                <div className="space-y-3.5">
                  <label className="flex items-start gap-3.5 p-3 rounded-xl border border-gray-50 bg-gray-50/30 hover:bg-gray-50 transition-colors cursor-pointer">
                    <input
                      type="checkbox"
                      className="mt-1 accent-primary"
                      checked={escalateContacts}
                      onChange={(e) => setEscalateContacts(e.target.checked)}
                      disabled={!isEnabled}
                    />
                    <div>
                      <p className="text-body-sm font-bold text-text-primary">Eskalasi ke Kontak Darurat</p>
                      <p className="text-xs text-text-secondary mt-0.5">Kirimkan SMS & lokasi GPS darurat ke keluarga jika Anda melewati batas respons.</p>
                    </div>
                  </label>

                  <label className="flex items-start gap-3.5 p-3 rounded-xl border border-gray-50 bg-gray-50/30 hover:bg-gray-50 transition-colors cursor-pointer">
                    <input
                      type="checkbox"
                      className="mt-1 accent-primary"
                      checked={escalate119}
                      onChange={(e) => setEscalate119(e.target.checked)}
                      disabled={!isEnabled}
                    />
                    <div>
                      <p className="text-body-sm font-bold text-text-primary flex items-center gap-1.5">
                        Eskalasi ke Layanan Medis Darurat 119
                        <Badge variant="urgent" className="text-[9px] px-1.5 py-0.5">Premium Only</Badge>
                      </p>
                      <p className="text-xs text-text-secondary mt-0.5">Langsung memesankan ambulans 119 ke lokasi GPS terdaftar Anda dalam skenario gawat darurat.</p>
                    </div>
                  </label>
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <Button type="submit" className="w-full sm:w-auto px-8" isLoading={saving} disabled={!isEnabled}>
                  <Save className="w-4 h-4 mr-1.5" /> Simpan Pengaturan
                </Button>
              </div>
            </Card>
          </form>
        </div>

        {/* Right Side: Log History & Simulation */}
        <div className="space-y-6">
          {/* Simulation Box */}
          <Card className="bg-gradient-to-br from-warning-light/50 to-danger-light/30 border border-warning/20">
            <div className="flex gap-2 items-center text-warning-dark mb-2">
              <AlertTriangle className="w-5 h-5 shrink-0" />
              <h4 className="font-heading font-bold text-body">Simulasi Proteksi</h4>
            </div>
            <p className="text-xs text-text-primary mb-4 leading-relaxed">
              Ingin menguji apakah eskalasi darurat JagaDiri berfungsi? Anda dapat menyimulasikan check-in yang terlewat secara instan di sini.
            </p>
            <Button size="sm" variant="danger" className="w-full">
              <PlayCircle className="w-4 h-4 mr-1.5" /> Uji Simulasikan Alarm
            </Button>
          </Card>

          {/* Logs */}
          <Card className="space-y-4">
            <h4 className="font-heading font-bold text-body text-text-primary border-b border-gray-100 pb-3">Riwayat Check-In</h4>
            <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
              {history.map((log) => (
                <div key={log.id} className="p-3.5 rounded-xl border border-gray-50 flex justify-between items-center gap-3 bg-surface">
                  <div>
                    <p className="text-xs text-text-secondary">
                      {new Date(log.scheduled_at).toLocaleDateString("id-ID", {
                        weekday: "short",
                        day: "numeric",
                        month: "short"
                      })}
                    </p>
                    <p className="text-body-sm font-bold text-text-primary mt-0.5">
                      {log.status === "responded" ? "Direspons" : "Telah Eskalasi"}
                    </p>
                  </div>
                  <Badge variant={log.status === "responded" ? "success" : "danger"}>
                    {log.status === "responded" ? `😊 Skor: ${log.mood_score}` : "Alarm"}
                  </Badge>
                </div>
              ))}
            </div>
          </Card>
        </div>

      </div>
    </div>
  );
}
