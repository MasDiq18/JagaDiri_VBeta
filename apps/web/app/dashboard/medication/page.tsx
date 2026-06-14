"use client";

import { useState, useEffect } from "react";
import { Calendar, Clock, PlusCircle, CheckCircle2, ChevronRight, Activity, TrendingUp } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { apiService } from "@/lib/api";

export default function MedicationPage() {
  const [loading, setLoading] = useState(true);
  const [reminders, setReminders] = useState<any[]>([]);
  const [report, setReport] = useState<any>(null);

  // Form states
  const [medicationName, setMedicationName] = useState("");
  const [dosage, setDosage] = useState("");
  const [timesPerDay, setTimesPerDay] = useState(1);
  const [time1, setTime1] = useState("08:00");
  const [time2, setTime2] = useState("20:00");
  const [withFood, setWithFood] = useState(true);
  const [notes, setNotes] = useState("");

  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [addError, setAddError] = useState("");

  async function loadData() {
    try {
      const list = await apiService.getReminders();
      setReminders(list);
      const rep = await apiService.getMedAdherenceReport();
      setReport(rep);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const handleAddReminder = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");

    const reminderTimes = [time1];
    if (timesPerDay > 1) reminderTimes.push(time2);

    try {
      await apiService.createReminder({
        medication_name: medicationName,
        dosage,
        times_per_day: timesPerDay,
        reminder_times: reminderTimes,
        with_food: withFood,
        start_date: new Date().toISOString().split("T")[0],
        notes
      });
      
      // Reset form
      setMedicationName("");
      setDosage("");
      setTimesPerDay(1);
      setTime1("08:00");
      setNotes("");

      setMessage("Jadwal pengingat obat berhasil ditambahkan.");
      setTimeout(() => setMessage(""), 3000);
      setAddError("");
      await loadData();
    } catch (err) {
      setAddError("Gagal menambahkan pengingat obat. Silakan coba lagi.");
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
        <h2 className="text-heading-xl font-bold text-text-primary">💊 Jadwal & Pengingat Obat (MedReminder)</h2>
        <p className="text-text-secondary text-body-sm mt-1">Kelola obat rutin Anda, dapatkan notifikasi tepat waktu, dan pantau tingkat kepatuhan minum obat Anda.</p>
      </div>

      {/* Adherence Overview Banner */}
      {report && (
        <div className="grid sm:grid-cols-4 gap-6">
          <Card className="text-center p-5 space-y-1 bg-gradient-to-br from-primary-50 to-primary-100/30 border border-primary-200">
            <p className="text-xs font-bold text-primary uppercase tracking-wider">Persentase Kepatuhan</p>
            <p className="text-heading-2xl font-extrabold text-primary">{report.persentase_kepatuhan}%</p>
            <p className="text-[10px] text-text-secondary">Target: &gt;90% untuk efektivitas optimal</p>
          </Card>
          
          <Card className="text-center p-5 space-y-1">
            <p className="text-xs font-bold text-text-secondary uppercase tracking-wider">Total Jadwal</p>
            <p className="text-heading-2xl font-extrabold text-text-primary">{report.total_jadwal}</p>
            <p className="text-[10px] text-text-secondary">Jadwal tercatat</p>
          </Card>

          <Card className="text-center p-5 space-y-1">
            <p className="text-xs font-bold text-text-secondary uppercase tracking-wider">Diminum</p>
            <p className="text-heading-2xl font-extrabold text-success">{report.total_diminum}</p>
            <p className="text-[10px] text-text-secondary">Tepat waktu</p>
          </Card>

          <Card className="text-center p-5 space-y-1">
            <p className="text-xs font-bold text-text-secondary uppercase tracking-wider">Dilewati / Terlambat</p>
            <p className="text-heading-2xl font-extrabold text-danger">{report.total_dilewati}</p>
            <p className="text-[10px] text-text-secondary">Perlu perhatian lebih</p>
          </Card>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-8">
        
        {/* Left Side: Reminders list & Adherence Detail */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="space-y-4">
            <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3">Daftar Obat Aktif</h3>
            
            <div className="space-y-4">
              {reminders.length > 0 ? (
                reminders.map((rem) => (
                  <div key={rem.id} className="p-4 rounded-xl border border-gray-100 bg-surface flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div className="flex gap-3.5 items-center">
                      <div className="w-10 h-10 rounded-full bg-secondary-light text-secondary flex items-center justify-center shrink-0">
                        <Clock className="w-5 h-5" />
                      </div>
                      <div>
                        <p className="font-bold text-text-primary text-body">{rem.medication_name}</p>
                        <p className="text-xs text-text-secondary mt-0.5">
                          Dosis: {rem.dosage || "1 tablet"} • Frekuensi: {rem.times_per_day}x sehari • {rem.with_food ? "Sesudah Makan" : "Sebelum Makan"}
                        </p>
                        {rem.notes && <p className="text-[11px] text-primary font-semibold mt-1">📝 {rem.notes}</p>}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {rem.reminder_times?.map((time: string) => (
                        <Badge key={time} variant="outline" className="font-mono bg-gray-50 text-text-primary border-gray-200">
                          {time}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <p className="text-text-secondary text-body-sm">Belum ada pengingat obat yang ditambahkan.</p>
                </div>
              )}
            </div>
          </Card>

          {/* Adherence Per Medication Report */}
          {report && report.detail_per_obat && (
            <Card className="space-y-4">
              <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3 flex items-center gap-1.5">
                <TrendingUp className="w-5 h-5 text-primary" />
                Tren Kepatuhan per Obat
              </h3>
              
              <div className="space-y-4">
                {report.detail_per_obat.map((item: any) => (
                  <div key={item.reminder_id} className="space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-text-primary">{item.medication_name}</span>
                      <span className="font-bold text-primary">{item.persentase}% kepatuhan</span>
                    </div>
                    {/* Progress bar */}
                    <div className="h-2.5 w-full bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full transition-all duration-500 ${
                          item.persentase >= 90 ? "bg-success" : item.persentase >= 75 ? "bg-warning" : "bg-danger"
                        }`}
                        style={{ width: `${item.persentase}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Right Side: Add Medication Form */}
        <div>
          <Card className="space-y-4">
            <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3">Tambah Pengingat</h3>
            
            {addError && (
              <div className="p-3.5 rounded-xl bg-danger-light border border-danger/30 text-danger text-xs">
                {addError}
              </div>
            )}

            {message && (
              <div className="p-3.5 rounded-xl bg-success-light border border-success/30 text-success text-xs">
                {message}
              </div>
            )}

            <form onSubmit={handleAddReminder} className="space-y-4">
              <Input
                label="Nama Obat"
                placeholder="Aspirin, Parasetamol, dll"
                value={medicationName}
                onChange={(e) => setMedicationName(e.target.value)}
                required
              />

              <Input
                label="Dosis (misal: 1 tablet, 500mg)"
                placeholder="1 tablet"
                value={dosage}
                onChange={(e) => setDosage(e.target.value)}
                required
              />

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-text-primary mb-1.5">Frekuensi Harian</label>
                  <select
                    className="input-field bg-white text-body-sm"
                    value={timesPerDay}
                    onChange={(e) => setTimesPerDay(Number(e.target.value))}
                  >
                    <option value={1}>1x Sehari</option>
                    <option value={2}>2x Sehari</option>
                    <option value={3}>3x Sehari</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-semibold text-text-primary mb-1.5">Makan</label>
                  <select
                    className="input-field bg-white text-body-sm"
                    value={withFood ? "after" : "before"}
                    onChange={(e) => setWithFood(e.target.value === "after")}
                  >
                    <option value="after">Sesudah Makan</option>
                    <option value="before">Sebelum Makan</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 border-t border-gray-100 pt-4">
                <div>
                  <label className="block text-xs font-bold text-text-secondary uppercase mb-1.5">Alarm 1</label>
                  <input
                    type="time"
                    className="input-field text-body-sm"
                    value={time1}
                    onChange={(e) => setTime1(e.target.value)}
                    required
                  />
                </div>

                {timesPerDay > 1 && (
                  <div>
                    <label className="block text-xs font-bold text-text-secondary uppercase mb-1.5">Alarm 2</label>
                    <input
                      type="time"
                      className="input-field text-body-sm"
                      value={time2}
                      onChange={(e) => setTime2(e.target.value)}
                      required
                    />
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-semibold text-text-primary mb-1.5">Catatan (Opsional)</label>
                <input
                  type="text"
                  placeholder="Contoh: Diminum dengan air hangat"
                  className="input-field text-body-sm"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </div>

              <Button type="submit" className="w-full" isLoading={saving}>
                <PlusCircle className="w-4 h-4 mr-1.5" /> Simpan Pengingat
              </Button>
            </form>
          </Card>
        </div>

      </div>
    </div>
  );
}
