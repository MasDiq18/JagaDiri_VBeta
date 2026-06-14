"use client";

import { useState, useEffect } from "react";
import { Search, Filter, MessageSquare, Video, Home, Phone, Star, AlertCircle, Plus, Calendar } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Modal } from "@/components/ui/modal";
import { Input } from "@/components/ui/input";
import { apiService } from "@/lib/api";

const SPECIALIZATIONS = [
  "Dokter Umum",
  "Spesialis Penyakit Dalam",
  "Kardiologi",
  "Neurologi",
  "Psikiater",
  "Obstetri & Ginekologi",
  "Anak",
  "Mata"
];

export default function ConsultationPage() {
  const [loading, setLoading] = useState(true);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);

  // Filter states
  const [search, setSearch] = useState("");
  const [specFilter, setSpecFilter] = useState("");
  const [onlineFilter, setOnlineFilter] = useState<boolean | null>(null);

  // Booking Modal states
  const [selectedDoctor, setSelectedDoctor] = useState<any>(null);
  const [showBookingModal, setShowBookingModal] = useState(false);
  
  // Booking Form states
  const [consultType, setConsultType] = useState("chat");
  const [scheduledDate, setScheduledDate] = useState("");
  const [scheduledTime, setScheduledTime] = useState("");
  const [chiefComplaint, setChiefComplaint] = useState("");
  const [patientNotes, setPatientNotes] = useState("");

  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingError, setBookingError] = useState("");

  async function loadData() {
    try {
      const docList = await apiService.getDoctors();
      setDoctors(docList);
      const hist = await apiService.getConsultations();
      setHistory(hist);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const handleOpenBooking = (doc: any) => {
    setSelectedDoctor(doc);
    setShowBookingModal(true);
  };

  const handleBookSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDoctor) return;
    setBookingLoading(true);

    const datetimeStr = scheduledDate && scheduledTime 
      ? new Date(`${scheduledDate}T${scheduledTime}`).toISOString()
      : new Date().toISOString();

    setBookingError("");
    try {
      await apiService.bookConsultation({
        doctor_id: selectedDoctor.id,
        type: consultType,
        scheduled_at: datetimeStr,
        chief_complaint: chiefComplaint,
        patient_notes: patientNotes,
        is_urgent: false
      });
      setShowBookingModal(false);
      // Reset form
      setConsultType("chat");
      setScheduledDate("");
      setScheduledTime("");
      setChiefComplaint("");
      setPatientNotes("");
      setSelectedDoctor(null);
      // Reload history
      await loadData();
    } catch (err) {
      setBookingError("Gagal melakukan pemesanan konsultasi. Silakan coba lagi.");
    } finally {
      setBookingLoading(false);
    }
  };

  // Filter logic
  const filteredDoctors = doctors.filter(doc => {
    const matchesSearch = doc.full_name.toLowerCase().includes(search.toLowerCase()) ||
                          doc.specialization.toLowerCase().includes(search.toLowerCase());
    const matchesSpec = specFilter ? doc.specialization === specFilter : true;
    const matchesOnline = onlineFilter !== null ? doc.is_online === onlineFilter : true;
    return matchesSearch && matchesSpec && matchesOnline;
  });

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
        <h2 className="text-heading-xl font-bold text-text-primary">🩺 Konsultasi Dokter Online</h2>
        <p className="text-text-secondary text-body-sm mt-1">Konsultasikan keluhan kesehatan Anda dengan dokter umum atau spesialis terverifikasi di Indonesia.</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        
        {/* Doctors Search & List */}
        <div className="lg:col-span-2 space-y-6">
          {/* Search bar & Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-secondary" />
              <input
                type="text"
                placeholder="Cari dokter berdasarkan nama atau spesialisasi..."
                className="input-field pl-12"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            
            <select
              className="input-field sm:w-56 bg-white"
              value={specFilter}
              onChange={(e) => setSpecFilter(e.target.value)}
            >
              <option value="">Semua Spesialisasi</option>
              {SPECIALIZATIONS.map(spec => (
                <option key={spec} value={spec}>{spec}</option>
              ))}
            </select>
          </div>

          {/* Quick Specialization Tags */}
          <div className="flex gap-2 overflow-x-auto pb-1 max-w-full">
            <Button
              variant={specFilter === "" ? "primary" : "outline"}
              size="sm"
              onClick={() => setSpecFilter("")}
            >
              Semua
            </Button>
            {SPECIALIZATIONS.slice(0, 4).map((spec) => (
              <Button
                key={spec}
                variant={specFilter === spec ? "primary" : "outline"}
                size="sm"
                onClick={() => setSpecFilter(spec)}
              >
                {spec.replace("Spesialis ", "")}
              </Button>
            ))}
          </div>

          {/* Doctors Cards */}
          <div className="space-y-4">
            {filteredDoctors.length > 0 ? (
              filteredDoctors.map((doc) => (
                <div 
                  key={doc.id}
                  className="p-5 bg-surface rounded-2xl border border-gray-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:shadow-card hover:-translate-y-[2px] transition-all duration-300"
                >
                  <div className="flex gap-4 items-start">
                    <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary-400 to-secondary-500 flex items-center justify-center text-white text-lg font-bold shrink-0 shadow-sm">
                      {doc.full_name.split(" ")[1]?.charAt(0) || "D"}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-bold text-text-primary text-body-lg">{doc.full_name}</p>
                        <Badge variant={doc.is_online ? "success" : "outline"} dot>
                          {doc.is_online ? "Online" : "Offline"}
                        </Badge>
                      </div>
                      <p className="text-primary text-body-sm font-semibold mt-0.5">{doc.specialization}</p>
                      <div className="flex items-center gap-1.5 mt-2 text-xs text-text-secondary">
                        <Star className="w-4 h-4 text-warning fill-warning" />
                        <span className="font-bold text-text-primary">{doc.rating}</span>
                        <span>({doc.total_reviews || 12} ulasan)</span>
                      </div>
                    </div>
                  </div>
                  <div className="w-full sm:w-auto flex flex-col items-end gap-2 border-t border-gray-50 pt-3 sm:border-none sm:pt-0">
                    <p className="text-xs text-text-secondary">Mulai dari</p>
                    <p className="font-bold text-text-primary">
                      Rp {(doc.consultation_fee_general || 35000).toLocaleString("id-ID")}
                    </p>
                    <Button onClick={() => handleOpenBooking(doc)} size="sm" className="w-full sm:w-auto mt-1">
                      Konsultasi
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <AlertCircle className="w-10 h-10 mx-auto text-text-secondary" />
                <p className="text-text-secondary mt-2 text-body-sm font-semibold">Tidak ada dokter yang cocok dengan kriteria filter.</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Side: Booking History */}
        <div className="space-y-6">
          <Card className="space-y-4">
            <h3 className="font-heading font-bold text-body text-text-primary border-b border-gray-100 pb-3">Riwayat Konsultasi</h3>
            
            <div className="space-y-3 max-h-[450px] overflow-y-auto pr-1">
              {history.length > 0 ? (
                history.map((con) => (
                  <div key={con.id} className="p-4 rounded-xl border border-gray-100 bg-surface space-y-3 text-body-sm">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-bold text-text-primary">{con.doctor_name}</p>
                        <p className="text-xs text-primary font-semibold mt-0.5">{con.specialization}</p>
                      </div>
                      <Badge variant={
                        con.status === "completed" ? "success" :
                        con.status === "ongoing" ? "primary" :
                        con.status === "cancelled" || con.status === "no_show" ? "danger" :
                        "secondary"
                      }>
                        {con.status === "pending" ? "Menunggu Konfirmasi" :
                         con.status === "confirmed" ? "Dikonfirmasi" :
                         con.status === "ongoing" ? "Berlangsung" :
                         con.status === "completed" ? "Selesai" :
                         con.status === "cancelled" ? "Dibatalkan" :
                         con.status === "no_show" ? "Tidak Hadir" :
                         con.status}
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between text-xs text-text-secondary pt-1.5 border-t border-gray-50">
                      <span className="flex items-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5 text-primary" />
                        {new Date(con.scheduled_at).toLocaleDateString("id-ID", {
                          day: "numeric",
                          month: "short"
                        })}
                      </span>
                      <span className="flex items-center gap-1">
                        {con.type === "chat" && <MessageSquare className="w-3.5 h-3.5 text-primary" />}
                        {con.type === "video" && <Video className="w-3.5 h-3.5 text-primary" />}
                        {con.type === "home_visit" && <Home className="w-3.5 h-3.5 text-primary" />}
                        {con.type === "phone" && <Phone className="w-3.5 h-3.5 text-primary" />}
                        <span className="capitalize">{con.type.replace("_", " ")}</span>
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <p className="text-text-secondary text-xs">Belum ada riwayat konsultasi.</p>
                </div>
              )}
            </div>
          </Card>
        </div>

      </div>

      {/* Booking Form Modal */}
      <Modal
        isOpen={showBookingModal}
        onClose={() => setShowBookingModal(false)}
        title={`Pesan Konsultasi: ${selectedDoctor?.full_name}`}
        size="md"
      >
        {selectedDoctor && (
          <form onSubmit={handleBookSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-1.5">Tipe Konsultasi</label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: "chat", label: "Chat Medis", icon: MessageSquare },
                  { id: "video", label: "Video Call", icon: Video },
                  { id: "home_visit", label: "Kunjungan Rumah", icon: Home },
                  { id: "phone", label: "Telepon", icon: Phone }
                ].map(item => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setConsultType(item.id)}
                      className={`flex items-center gap-2 p-3.5 rounded-xl border text-left transition-all ${
                        consultType === item.id 
                          ? "border-primary bg-primary-light text-primary font-bold shadow-sm" 
                          : "border-gray-100 hover:border-gray-200"
                      }`}
                    >
                      <Icon className="w-4 h-4 text-primary shrink-0" />
                      <span className="text-xs">{item.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-1.5">Pilih Tanggal</label>
                <input
                  type="date"
                  className="input-field text-body-sm"
                  value={scheduledDate}
                  onChange={(e) => setScheduledDate(e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-1.5">Pilih Jam</label>
                <input
                  type="time"
                  className="input-field text-body-sm"
                  value={scheduledTime}
                  onChange={(e) => setScheduledTime(e.target.value)}
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-1.5">Keluhan Utama</label>
              <textarea
                placeholder="Deskripsikan gejala yang Anda rasakan secara detail (min. 10 karakter)..."
                className="input-field text-body-sm min-h-[80px] py-3.5"
                value={chiefComplaint}
                onChange={(e) => setChiefComplaint(e.target.value)}
                required
                minLength={10}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-1.5">Catatan Tambahan (Opsional)</label>
              <textarea
                placeholder="Riwayat obat yang dikonsumsi, alergi, atau catatan lainnya..."
                className="input-field text-body-sm min-h-[60px] py-3.5"
                value={patientNotes}
                onChange={(e) => setPatientNotes(e.target.value)}
              />
            </div>

            {bookingError && (
              <div className="p-3.5 rounded-xl bg-danger-light border border-danger/30 text-danger text-body-sm">
                {bookingError}
              </div>
            )}

            <div className="flex gap-3 pt-3">
              <Button type="button" variant="ghost" className="flex-1" onClick={() => { setShowBookingModal(false); setBookingError(""); }}>
                Batal
              </Button>
              <Button type="submit" className="flex-1" isLoading={bookingLoading}>
                Pesan & Bayar
              </Button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
}
