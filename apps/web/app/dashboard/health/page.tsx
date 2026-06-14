"use client";

import { useState, useEffect } from "react";
import { 
  Heart, 
  Activity, 
  FileText, 
  UserCheck, 
  Plus, 
  Edit2, 
  QrCode, 
  Download, 
  PlusCircle, 
  Printer, 
  Calendar, 
  AlertCircle 
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { apiService } from "@/lib/api";

export default function HealthPage() {
  const [activeTab, setActiveTab] = useState("profile");
  const [loading, setLoading] = useState(true);

  // Medical Profile State
  const [medProfile, setMedProfile] = useState<any>(null);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [bloodType, setBloodType] = useState("");
  const [allergies, setAllergies] = useState<string[]>([]);
  const [chronicConditions, setChronicConditions] = useState<string[]>([]);
  const [contactName, setContactName] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [contactRelation, setContactRelation] = useState("");
  const [bpjsNumber, setBpjsNumber] = useState("");
  const [insuranceProvider, setInsuranceProvider] = useState("");

  // Vitals State
  const [vitals, setVitals] = useState<any[]>([]);
  
  // Vital Form State
  const [metricType, setMetricType] = useState("blood_pressure");
  const [valueNumeric, setValueNumeric] = useState("");
  const [valueSystolic, setValueSystolic] = useState("");
  const [valueDiastolic, setValueDiastolic] = useState("");
  const [vitalNotes, setVitalNotes] = useState("");

  // MedCard State
  const [medCard, setMedCard] = useState<any>(null);

  const [savingProfile, setSavingProfile] = useState(false);
  const [savingVital, setSavingVital] = useState(false);
  const [profileError, setProfileError] = useState("");
  const [profileMsg, setProfileMsg] = useState("");
  const [vitalError, setVitalError] = useState("");

  async function loadData() {
    try {
      const prof = await apiService.getMedCard();
      setMedProfile(prof);
      setBloodType(prof.blood_type || "O+");
      setAllergies(prof.allergies || []);
      setChronicConditions(prof.chronic_conditions || []);
      setContactName(prof.emergency_contact_name || "");
      setContactPhone(prof.emergency_contact_phone || "");
      setContactRelation(prof.emergency_contact_relation || "");
      setBpjsNumber(prof.bpjs_number || "");
      setInsuranceProvider(prof.insurance_provider || "");

      const vt = await apiService.getVitals();
      setVitals(vt);

      setMedCard(prof);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingProfile(true);
    setProfileError("");
    try {
      // Simpan profil medis dengan API yang benar
      await apiService.updateMedProfile({
        blood_type: bloodType,
        allergies,
        chronic_conditions: chronicConditions,
        bpjs_number: bpjsNumber,
        insurance_provider: insuranceProvider,
        emergency_contact_name: contactName,
        emergency_contact_phone: contactPhone,
        emergency_contact_relation: contactRelation,
      });
      setIsEditingProfile(false);
      setProfileMsg("Profil medis berhasil disimpan.");
      setTimeout(() => setProfileMsg(""), 3000);
      await loadData();
    } catch (err) {
      setProfileError("Gagal menyimpan profil medis. Silakan coba lagi.");
    } finally {
      setSavingProfile(false);
    }
  };

  const handleAddVital = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingVital(true);

    let unit = "N/A";
    if (metricType === "blood_pressure") unit = "mmHg";
    else if (metricType === "heart_rate") unit = "bpm";
    else if (metricType === "temperature") unit = "°C";
    else if (metricType === "blood_sugar") unit = "mg/dL";

    try {
      await apiService.addVital({
        metric_type: metricType,
        value_numeric: valueNumeric ? Number(valueNumeric) : undefined,
        value_systolic: valueSystolic ? Number(valueSystolic) : undefined,
        value_diastolic: valueDiastolic ? Number(valueDiastolic) : undefined,
        unit,
        notes: vitalNotes
      });
      // Reset form
      setValueNumeric("");
      setValueSystolic("");
      setValueDiastolic("");
      setVitalNotes("");
      setVitalError("");
      await loadData();
    } catch (err) {
      setVitalError("Gagal menambahkan tanda vital. Silakan coba lagi.");
    } finally {
      setSavingVital(false);
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
        <h2 className="text-heading-xl font-bold text-text-primary">🏥 Pusat Rekam Medis & Keselamatan</h2>
        <p className="text-text-secondary text-body-sm mt-1">Kelola informasi rekam medis pribadi, pantau tanda vital, dan dapatkan MedCard penyelamat Anda.</p>
      </div>

      {/* Tabs Switcher */}
      <div className="flex border-b border-gray-100 max-w-full overflow-x-auto pb-1 gap-2">
        {[
          { id: "profile", label: "Profil Medis", icon: UserCheck },
          { id: "vitals", label: "Tanda Vital", icon: Activity },
          { id: "medcard", label: "MedCard Darurat", icon: FileText }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-6 py-3 border-b-2 font-semibold text-body-sm transition-all ${
                activeTab === tab.id
                  ? "border-primary text-primary"
                  : "border-transparent text-text-secondary hover:text-text-primary"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Profile Tab */}
      {activeTab === "profile" && (
        <div className="grid md:grid-cols-3 gap-8">
          <div className="md:col-span-2">
            <Card className="space-y-6">
              <div className="flex justify-between items-center border-b border-gray-100 pb-4">
                <h3 className="font-heading font-bold text-heading-md text-text-primary">Profil Medis Mandiri</h3>
                {!isEditingProfile && (
                  <Button onClick={() => setIsEditingProfile(true)} size="sm" variant="outline">
                    <Edit2 className="w-4 h-4 mr-1.5" /> Sunting Profil
                  </Button>
                )}
              </div>

              {profileMsg && (
                <div className="p-3.5 rounded-xl bg-success-light border border-success/30 text-success text-body-sm">
                  {profileMsg}
                </div>
              )}
              {profileError && (
                <div className="p-3.5 rounded-xl bg-danger-light border border-danger/30 text-danger text-body-sm">
                  {profileError}
                </div>
              )}

              {!isEditingProfile ? (
                <div className="grid sm:grid-cols-2 gap-6 text-body-sm">
                  <div className="space-y-4">
                    <div>
                      <p className="text-xs font-semibold text-text-secondary uppercase">Golongan Darah</p>
                      <p className="font-bold text-heading-md text-text-primary mt-1">{bloodType || "Belum diisi"}</p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-text-secondary uppercase">Alergi Obat/Makanan</p>
                      <div className="flex flex-wrap gap-1.5 mt-1.5">
                        {allergies.length > 0 ? (
                          allergies.map(alg => (
                            <Badge key={alg} variant="danger">{alg}</Badge>
                          ))
                        ) : (
                          <span className="text-text-secondary">Tidak ada alergi</span>
                        )}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-text-secondary uppercase">Riwayat Penyakit Kronis</p>
                      <div className="flex flex-wrap gap-1.5 mt-1.5">
                        {chronicConditions.length > 0 ? (
                          chronicConditions.map(cond => (
                            <Badge key={cond} variant="warning">{cond}</Badge>
                          ))
                        ) : (
                          <span className="text-text-secondary">Tidak ada kondisi kronis</span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <p className="text-xs font-semibold text-text-secondary uppercase">Kontak Darurat Utama</p>
                      <p className="font-bold text-text-primary mt-1">{contactName || "Belum diisi"}</p>
                      <p className="text-text-secondary text-xs mt-0.5">{contactPhone} ({contactRelation})</p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-text-secondary uppercase">Nomor Asuransi / BPJS</p>
                      <p className="font-bold text-text-primary mt-1">{bpjsNumber || "Belum diisi"}</p>
                      <p className="text-text-secondary text-xs mt-0.5">{insuranceProvider}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleProfileSave} className="space-y-4">
                  <div className="grid sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-text-primary mb-1.5">Golongan Darah</label>
                      <select
                        className="input-field bg-white text-body-sm"
                        value={bloodType}
                        onChange={(e) => setBloodType(e.target.value)}
                      >
                        {["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                    <Input
                      label="Nomor BPJS"
                      value={bpjsNumber}
                      onChange={(e) => setBpjsNumber(e.target.value)}
                    />
                  </div>

                  <div className="grid sm:grid-cols-3 gap-4">
                    <div className="sm:col-span-2">
                      <Input
                        label="Kontak Darurat Utama"
                        value={contactName}
                        onChange={(e) => setContactName(e.target.value)}
                      />
                    </div>
                    <Input
                      label="Hubungan"
                      value={contactRelation}
                      onChange={(e) => setContactRelation(e.target.value)}
                    />
                  </div>
                  <Input
                    label="Nomor Telepon Kontak"
                    value={contactPhone}
                    onChange={(e) => setContactPhone(e.target.value)}
                  />

                  <div className="flex gap-2 justify-end pt-3">
                    <Button type="button" variant="ghost" onClick={() => setIsEditingProfile(false)}>
                      Batal
                    </Button>
                    <Button type="submit" isLoading={savingProfile}>
                      Simpan Profil
                    </Button>
                  </div>
                </form>
              )}
            </Card>
          </div>
          <div>
            <Card className="bg-gradient-to-br from-primary-50 to-secondary-50 border border-primary-100">
              <h4 className="font-heading font-bold text-body text-text-primary flex items-center gap-1.5">
                <AlertCircle className="w-5 h-5 text-primary shrink-0" />
                Mengapa ini penting?
              </h4>
              <p className="text-xs text-text-primary leading-relaxed mt-3">
                Informasi ini tersimpan aman secara terenkripsi. Ketika Anda mengaktifkan SOS atau QR Code MedCard Anda dipindai oleh paramedis saat pingsan, info medis dasar ini akan langsung membantu tim penyelamat memberikan tindakan pertama yang tepat.
              </p>
            </Card>
          </div>
        </div>
      )}

      {/* Vitals Tab */}
      {activeTab === "vitals" && (
        <div className="grid md:grid-cols-3 gap-8">
          
          {/* Add Vital Form */}
          <div>
            <Card className="space-y-4">
              <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3">Catat Tanda Vital</h3>
              <form onSubmit={handleAddVital} className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-text-primary mb-1.5">Tipe Metrik</label>
                  <select
                    className="input-field bg-white text-body-sm"
                    value={metricType}
                    onChange={(e) => setMetricType(e.target.value)}
                  >
                    <option value="blood_pressure">Tekanan Darah (Tensi)</option>
                    <option value="heart_rate">Detak Jantung (Nadi)</option>
                    <option value="temperature">Suhu Tubuh</option>
                    <option value="blood_sugar">Gula Darah</option>
                  </select>
                </div>

                {metricType === "blood_pressure" ? (
                  <div className="grid grid-cols-2 gap-3">
                    <Input
                      label="Sistolik (Atas)"
                      type="number"
                      placeholder="120"
                      value={valueSystolic}
                      onChange={(e) => setValueSystolic(e.target.value)}
                      required
                    />
                    <Input
                      label="Diastolik (Bawah)"
                      type="number"
                      placeholder="80"
                      value={valueDiastolic}
                      onChange={(e) => setValueDiastolic(e.target.value)}
                      required
                    />
                  </div>
                ) : (
                  <Input
                    label={`Nilai Angka (${metricType === "temperature" ? "°C" : metricType === "heart_rate" ? "bpm" : "mg/dL"})`}
                    type="number"
                    step="0.1"
                    placeholder="Masukkan angka..."
                    value={valueNumeric}
                    onChange={(e) => setValueNumeric(e.target.value)}
                    required
                  />
                )}

                <div>
                  <label className="block text-sm font-semibold text-text-primary mb-1.5">Catatan tambahan</label>
                  <input
                    type="text"
                    placeholder="Contoh: Setelah bangun tidur, sebelum makan"
                    className="input-field text-body-sm"
                    value={vitalNotes}
                    onChange={(e) => setVitalNotes(e.target.value)}
                  />
                </div>

                {vitalError && (
                  <div className="p-3 rounded-xl bg-danger-light border border-danger/30 text-danger text-xs">
                    {vitalError}
                  </div>
                )}

                <Button type="submit" className="w-full" isLoading={savingVital}>
                  <PlusCircle className="w-4 h-4 mr-1.5" /> Catat Sekarang
                </Button>
              </form>
            </Card>
          </div>

          {/* Vitals Log list */}
          <div className="md:col-span-2">
            <Card className="space-y-4">
              <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3">Riwayat Log Tanda Vital</h3>
              <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
                {vitals.length > 0 ? (
                  vitals.map((v) => {
                    const isBP = v.metric_type === "blood_pressure";
                    const displayVal = isBP ? `${v.value_systolic}/${v.value_diastolic}` : v.value_numeric;
                    const name = isBP ? "Tekanan Darah" : v.metric_type === "heart_rate" ? "Detak Jantung" : v.metric_type === "temperature" ? "Suhu Tubuh" : "Gula Darah";
                    return (
                      <div key={v.id} className="p-4 rounded-xl border border-gray-100 bg-surface flex items-center justify-between gap-4">
                        <div className="flex gap-3 items-center">
                          <div className="w-10 h-10 rounded-full bg-primary-light text-primary flex items-center justify-center shrink-0">
                            <Activity className="w-5 h-5" />
                          </div>
                          <div>
                            <p className="font-bold text-text-primary text-body-sm">{name}</p>
                            <p className="text-[10px] text-text-secondary mt-0.5">
                              {new Date(v.created_at).toLocaleDateString("id-ID", {
                                day: "numeric",
                                month: "short",
                                hour: "2-digit",
                                minute: "2-digit"
                              })} • {v.notes || "Tanpa catatan"}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-heading-md font-extrabold text-primary">{displayVal}</p>
                          <p className="text-[10px] text-text-secondary">{v.unit}</p>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-center py-12">
                    <p className="text-text-secondary text-body-sm">Belum ada riwayat tanda vital yang dicatat.</p>
                  </div>
                )}
              </div>
            </Card>
          </div>

        </div>
      )}

      {/* MedCard Tab */}
      {activeTab === "medcard" && (
        <div className="grid md:grid-cols-2 gap-8 items-start">
          {/* Card Mock Render */}
          <div className="space-y-4">
            <div className="relative w-full max-w-sm aspect-[1.586/1] rounded-2xl bg-gradient-to-br from-primary-800 to-secondary-900 text-white p-6 shadow-glass-xl border border-white/20 flex flex-col justify-between overflow-hidden">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.06),transparent_50%)] pointer-events-none" />
              
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-heading font-extrabold text-lg tracking-tight">Jaga<span className="text-primary-300">Diri</span> MedCard</p>
                  <p className="text-[9px] uppercase tracking-widest text-white/50">Emergency Rescue Card</p>
                </div>
                <Badge variant="urgent" className="text-[9px] bg-red-600/90 text-white font-bold border-none">MEDIK</Badge>
              </div>

              <div>
                <p className="text-[10px] text-white/50 uppercase tracking-wider">Nama Lengkap</p>
                <p className="font-bold text-heading-md truncate">{medCard?.full_name}</p>
                <p className="text-[9px] text-white/60 mt-1">Lahir: {medCard?.date_of_birth} • Gol. Darah: <strong className="text-warning-light">{medCard?.blood_type || "O+"}</strong></p>
              </div>

              <div className="flex justify-between items-end border-t border-white/10 pt-3">
                <div>
                  <p className="text-[8px] text-white/50 uppercase">Kontak Darurat</p>
                  <p className="font-bold text-xs">{medCard?.emergency_contact_name || "Belum diisi"}</p>
                  <p className="text-[10px] text-white/75">{medCard?.emergency_contact_phone}</p>
                </div>
                {/* Simulated QR Code placeholder */}
                <div className="w-12 h-12 bg-white rounded-lg p-1 flex items-center justify-center shrink-0 shadow-md">
                  <QrCode className="w-10 h-10 text-primary-900" />
                </div>
              </div>
            </div>
            
            <div className="flex gap-3">
              <Button size="sm" variant="outline" className="flex-1">
                <Printer className="w-4 h-4 mr-1.5" /> Cetak Kartu
              </Button>
              <Button size="sm" variant="outline" className="flex-1">
                <Download className="w-4 h-4 mr-1.5" /> Unduh PDF
              </Button>
            </div>
          </div>

          {/* Guidelines */}
          <Card className="space-y-6">
            <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3">Cara Kerja MedCard</h3>
            <div className="space-y-4 text-body-sm text-text-primary">
              <div className="flex gap-3 items-start">
                <div className="w-8 h-8 rounded-full bg-primary-light text-primary font-bold flex items-center justify-center shrink-0">1</div>
                <div>
                  <p className="font-bold">Pasang di Layar Kunci (Lock Screen)</p>
                  <p className="text-xs text-text-secondary mt-0.5">Simpan gambar QR code MedCard Anda dan gunakan sebagai wallpaper lockscreen ponsel Anda.</p>
                </div>
              </div>

              <div className="flex gap-3 items-start">
                <div className="w-8 h-8 rounded-full bg-primary-light text-primary font-bold flex items-center justify-center shrink-0">2</div>
                <div>
                  <p className="font-bold">Scan Instan oleh Paramedis</p>
                  <p className="text-xs text-text-secondary mt-0.5">Jika terjadi kecelakaan atau Anda pingsan di jalan raya, paramedis dapat memindai QR code Anda tanpa membuka sandi ponsel.</p>
                </div>
              </div>

              <div className="flex gap-3 items-start">
                <div className="w-8 h-8 rounded-full bg-primary-light text-primary font-bold flex items-center justify-center shrink-0">3</div>
                <div>
                  <p className="font-bold">Akses Penyelamatan Cepat</p>
                  <p className="text-xs text-text-secondary mt-0.5">Halaman publik khusus akan menampilkan data alergi Anda dan nomor kontak keluarga yang harus dihubungi segera.</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
