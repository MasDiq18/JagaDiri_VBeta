"use client";

import { useState, useEffect } from "react";
import { Users, Mail, PlusCircle, Shield, Clock, Activity, Check, AlertCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { apiService } from "@/lib/api";

export default function FamilyPage() {
  const [loading, setLoading] = useState(true);
  const [connections, setConnections] = useState<any[]>([]);
  
  // Invite Form States
  const [email, setEmail] = useState("");
  const [relation, setRelation] = useState("");
  const [accessLevel, setAccessLevel] = useState("basic");
  
  // Sharing Permissions
  const [viewSafePing, setViewSafePing] = useState(true);
  const [viewMeds, setViewMeds] = useState(true);
  const [viewVitals, setViewVitals] = useState(false);
  
  const [inviting, setInviting] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Caregiver view state
  const [selectedMember, setSelectedMember] = useState<any>(null);
  const [memberStatus, setMemberStatus] = useState<any>(null);
  const [loadingMember, setLoadingMember] = useState(false);
  const [memberError, setMemberError] = useState("");

  async function loadData() {
    try {
      const list = await apiService.getFamilyConnections();
      setConnections(list);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const handleInviteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setInviting(true);
    setMessage("");
    setError("");

    try {
      const invite = await apiService.inviteFamilyMember({
        email,
        relation,
        access_level: accessLevel,
        can_view_safeping: viewSafePing,
        can_view_medication_adherence: viewMeds,
        can_view_vital_signs: viewVitals,
        can_view_consultation_history: false,
        can_view_mental_health: false
      });
      setMessage(`Undangan berhasil dikirim ke ${email}.`);
      setEmail("");
      setRelation("");
      setAccessLevel("basic");
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Gagal mengundang anggota keluarga. Pastikan email terdaftar.");
    } finally {
      setInviting(false);
    }
  };

  const handleViewMemberStatus = async (conn: any) => {
    setSelectedMember(conn);
    setLoadingMember(true);
    try {
      // Fetch mock/api status
      const statusRes = await apiService.getHealthInsights(); // simulated details
      setMemberStatus({
        full_name: conn.family_member_name,
        safeping_status: "responded",
        last_check_in: new Date().toISOString(),
        medication_adherence_pct: 93.3,
        last_vital_signs: {
          metric_type: "blood_pressure",
          value_systolic: 120,
          value_diastolic: 80,
          unit: "mmHg"
        }
      });
    } catch (err) {
      setMemberError("Gagal memuat status kesehatan anggota keluarga.");
    } finally {
      setLoadingMember(false);
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
        <h2 className="text-heading-xl font-bold text-text-primary">👥 Portal Keluarga & Caregiver</h2>
        <p className="text-text-secondary text-body-sm mt-1">
          Hubungkan akun JagaDiri Anda dengan anggota keluarga tercinta. Bagikan status keselamatan SafePing dan jadwal obat Anda kepada mereka secara terkontrol.
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        
        {/* Left Side: Connection list & Caregiver Status view */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="space-y-4">
            <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3">Koneksi Keluarga Terhubung</h3>
            
            <div className="space-y-3">
              {connections.length > 0 ? (
                connections.map((conn) => (
                  <div key={conn.id} className="p-4 rounded-xl border border-gray-100 bg-surface flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div className="flex gap-3.5 items-center">
                      <div className="w-10 h-10 rounded-full bg-primary-light text-primary flex items-center justify-center shrink-0 font-bold">
                        {conn.family_member_name?.charAt(0) || "F"}
                      </div>
                      <div>
                        <p className="font-bold text-text-primary text-body">{conn.family_member_name}</p>
                        <p className="text-xs text-text-secondary mt-0.5">
                          Hubungan: {conn.relation || "Keluarga"} • Level Akses: <span className="capitalize font-semibold text-primary">{conn.access_level}</span>
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
                      <Badge variant={conn.status === "active" ? "success" : "pending"}>
                        {conn.status === "active" ? "Aktif" : "Menunggu Persetujuan"}
                      </Badge>
                      {conn.status === "active" && (
                        <Button onClick={() => handleViewMemberStatus(conn)} size="sm" variant="outline">
                          Pantau Kesehatan
                        </Button>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <p className="text-text-secondary text-body-sm">Belum ada koneksi keluarga terhubung.</p>
                </div>
              )}
            </div>
          </Card>

          {/* Caregiver Detail Status Viewer */}
          {selectedMember && (
            <Card className="space-y-4 border border-secondary bg-secondary-light/10">
              <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3">
                Pemantauan Kesehatan Jauh: {selectedMember.family_member_name}
              </h3>
              
              {loadingMember ? (
                <div className="py-6 text-center">
                  <div className="w-6 h-6 border-2 border-secondary border-t-transparent rounded-full animate-spin mx-auto" />
                </div>
              ) : memberError ? (
                <div className="p-3.5 rounded-xl bg-danger-light border border-danger/30 text-danger text-xs">
                  {memberError}
                </div>
              ) : (
                memberStatus && (
                  <div className="grid sm:grid-cols-3 gap-6 text-body-sm">
                    <div className="p-4 rounded-xl bg-white border border-gray-100 space-y-1">
                      <p className="text-xs font-bold text-text-secondary uppercase">SafePing Check-In</p>
                      <p className="font-bold text-success text-body-lg flex items-center gap-1.5 mt-1">
                        <Check className="w-5 h-5 text-success" /> Direspons
                      </p>
                      <p className="text-[10px] text-text-secondary mt-1">Terakhir check-in: hari ini</p>
                    </div>

                    <div className="p-4 rounded-xl bg-white border border-gray-100 space-y-1">
                      <p className="text-xs font-bold text-text-secondary uppercase">Kepatuhan Obat</p>
                      <p className="font-bold text-primary text-body-lg mt-1">{memberStatus.medication_adherence_pct}%</p>
                      <p className="text-[10px] text-text-secondary mt-1">Kategori: Kepatuhan Baik</p>
                    </div>

                    <div className="p-4 rounded-xl bg-white border border-gray-100 space-y-1">
                      <p className="text-xs font-bold text-text-secondary uppercase">Tanda Vital Terakhir</p>
                      <p className="font-bold text-text-primary text-body-lg mt-1">
                        {memberStatus.last_vital_signs.value_systolic}/{memberStatus.last_vital_signs.value_diastolic}
                      </p>
                      <p className="text-[10px] text-text-secondary mt-1">Tensi ({memberStatus.last_vital_signs.unit})</p>
                    </div>
                  </div>
                )
              )}
            </Card>
          )}
        </div>

        {/* Right Side: Invite Family Member Form */}
        <div>
          <Card className="space-y-4">
            <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3">Hubungkan Keluarga</h3>
            
            {message && (
              <div className="p-3.5 rounded-xl bg-success-light border border-success/30 text-success text-xs">
                {message}
              </div>
            )}

            {error && (
              <div className="p-3.5 rounded-xl bg-danger-light border border-danger/30 text-danger text-xs flex gap-1.5 items-start">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleInviteSubmit} className="space-y-4">
              <Input
                label="Email Keluarga (Terdaftar)"
                placeholder="keluarga@email.com"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <Input
                label="Hubungan (misal: Anak, Ibu, Suami)"
                placeholder="Anak Kandung"
                value={relation}
                onChange={(e) => setRelation(e.target.value)}
                required
              />

              <div>
                <label className="block text-sm font-semibold text-text-primary mb-1.5">Level Akses Data</label>
                <select
                  className="input-field bg-white text-body-sm"
                  value={accessLevel}
                  onChange={(e) => setAccessLevel(e.target.value)}
                >
                  <option value="basic">Basic (Hanya SafePing)</option>
                  <option value="standard">Standard (SafePing + Obat)</option>
                  <option value="full">Full Access (Semua Data Medis)</option>
                </select>
              </div>

              {/* Data Sharing Checkbox Toggles */}
              <div className="space-y-3 pt-3 border-t border-gray-100">
                <label className="flex items-center gap-2.5 text-xs text-text-primary cursor-pointer">
                  <input
                    type="checkbox"
                    checked={viewSafePing}
                    onChange={(e) => setViewSafePing(e.target.checked)}
                    className="accent-primary"
                  />
                  <span>Bagikan Status SafePing Harian</span>
                </label>

                <label className="flex items-center gap-2.5 text-xs text-text-primary cursor-pointer">
                  <input
                    type="checkbox"
                    checked={viewMeds}
                    onChange={(e) => setViewMeds(e.target.checked)}
                    className="accent-primary"
                  />
                  <span>Bagikan Kepatuhan Obat (Reminder)</span>
                </label>

                <label className="flex items-center gap-2.5 text-xs text-text-primary cursor-pointer">
                  <input
                    type="checkbox"
                    checked={viewVitals}
                    onChange={(e) => setViewVitals(e.target.checked)}
                    className="accent-primary"
                  />
                  <span>Bagikan Log Tanda Vital</span>
                </label>
              </div>

              <Button type="submit" className="w-full" isLoading={inviting}>
                <PlusCircle className="w-4 h-4 mr-1.5" /> Kirim Undangan
              </Button>
            </form>
          </Card>
        </div>

      </div>
    </div>
  );
}
