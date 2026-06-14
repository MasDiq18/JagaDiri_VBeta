"use client";

import { useState } from "react";
import { Clock, Save, ShieldAlert, Check } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function DoctorSchedulePage() {
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const [activeDays, setActiveDays] = useState({
    1: true, // Senin
    2: true, // Selasa
    3: true, // Rabu
    4: true, // Kamis
    5: true, // Jumat
    6: false, // Sabtu
    0: false  // Minggu
  });

  const [startTime, setStartTime] = useState("08:00");
  const [endTime, setEndTime] = useState("16:00");

  const handleDayToggle = (day: number) => {
    setActiveDays(prev => ({
      ...prev,
      [day]: !(prev as any)[day]
    }));
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      setMessage("Jadwal praktik berhasil diperbarui.");
      setTimeout(() => setMessage(""), 3000);
    }, 1000);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h2 className="text-heading-xl font-bold text-text-primary">📅 Pengaturan Jadwal Praktik</h2>
        <p className="text-text-secondary text-body-sm mt-1">Konfigurasikan hari kerja dan jam operasional konsultasi Anda.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        <div className="md:col-span-2">
          <form onSubmit={handleSave}>
            <Card className="space-y-6">
              <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3">Hari & Jam Aktif</h3>

              {message && (
                <div className="p-3.5 rounded-xl bg-success-light border border-success/30 text-success text-xs flex items-center gap-1.5 font-semibold">
                  <Check className="w-4 h-4" />
                  <span>{message}</span>
                </div>
              )}

              {/* Days Checkboxes */}
              <div className="space-y-3">
                <label className="block text-sm font-semibold text-text-primary">Pilih Hari Aktif Praktik</label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {[
                    { id: 1, label: "Senin" },
                    { id: 2, label: "Selasa" },
                    { id: 3, label: "Rabu" },
                    { id: 4, label: "Kamis" },
                    { id: 5, label: "Jumat" },
                    { id: 6, label: "Sabtu" },
                    { id: 0, label: "Minggu" }
                  ].map(day => (
                    <button
                      key={day.id}
                      type="button"
                      onClick={() => handleDayToggle(day.id)}
                      className={`p-3 rounded-xl border text-center transition-all text-xs font-semibold ${
                        (activeDays as any)[day.id]
                          ? "border-primary bg-primary-light text-primary font-bold shadow-sm"
                          : "border-gray-100 text-text-secondary hover:border-gray-200"
                      }`}
                    >
                      {day.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Time inputs */}
              <div className="grid sm:grid-cols-2 gap-4 border-t border-gray-100 pt-6">
                <div>
                  <label className="block text-sm font-semibold text-text-primary mb-1.5">Jam Mulai</label>
                  <input
                    type="time"
                    className="input-field text-body-sm"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-text-primary mb-1.5">Jam Selesai</label>
                  <input
                    type="time"
                    className="input-field text-body-sm"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <Button type="submit" className="w-full sm:w-auto px-8" isLoading={saving}>
                  <Save className="w-4 h-4 mr-1.5" /> Simpan Jadwal
                </Button>
              </div>
            </Card>
          </form>
        </div>

        <div>
          <Card className="bg-gradient-to-br from-primary-50 to-secondary-50 border border-primary-100 p-5 space-y-3">
            <h4 className="font-bold text-body-sm text-text-primary flex gap-1.5 items-center">
              <ShieldAlert className="w-4 h-4 text-primary" /> Informasi Kalender
            </h4>
            <p className="text-xs text-text-primary leading-relaxed">
              Jadwal yang Anda tetapkan di sini akan langsung sinkron dengan daftar slot waktu pencarian dokter yang tampil di layar pasien JagaDiri.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
