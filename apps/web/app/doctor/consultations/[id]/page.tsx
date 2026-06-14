"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { MessageSquare, Heart, Clipboard, FileText, Send, User, ChevronLeft, Check } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

export default function DoctorConsultationDetail({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  // SOAP state
  const [subjective, setSubjective] = useState("");
  const [objective, setObjective] = useState("");
  const [assessment, setAssessment] = useState("");
  const [plan, setPlan] = useState("");

  // Chat state
  const [messages, setMessages] = useState<any[]>([
    { sender: "patient", text: "Halo Dokter, saya mengalami pusing hebat sejak kemarin malam di kepala bagian belakang.", time: "08:05" },
    { sender: "doctor", text: "Halo Budi, apakah pusingnya terasa berputar (vertigo) atau seperti diikat kencang?", time: "08:06" },
    { sender: "patient", text: "Terasa seperti diikat kencang dok, dan agak mual kalau dipaksa berdiri lama.", time: "08:07" }
  ]);
  const [inputMsg, setInputMsg] = useState("");

  const handleSend = () => {
    if (!inputMsg.trim()) return;
    setMessages(prev => [
      ...prev,
      { sender: "doctor", text: inputMsg, time: new Date().toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" }) }
    ]);
    setInputMsg("");
  };

  const handleSOAPSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setTimeout(() => {
      setSubmitting(false);
      setSubmitted(true);
    }, 1200);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" onClick={() => router.push("/doctor")} className="p-0 hover:bg-transparent text-text-secondary hover:text-text-primary">
          <ChevronLeft className="w-5 h-5 mr-1" /> Kembali ke Antrean
        </Button>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        
        {/* Left: Patient Info Card */}
        <div className="space-y-6">
          <Card className="space-y-4">
            <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3 flex items-center gap-1.5">
              <User className="w-5 h-5 text-primary" />
              Profil Medis Pasien
            </h3>

            <div className="space-y-4 text-body-sm text-text-primary">
              <div>
                <p className="text-[10px] font-bold text-text-secondary uppercase">Nama Pasien</p>
                <p className="font-bold text-text-primary mt-0.5">Budi Santoso</p>
              </div>
              <div>
                <p className="text-[10px] font-bold text-text-secondary uppercase">Umur / Tgl Lahir</p>
                <p className="font-semibold text-text-primary mt-0.5">30 tahun (17 Agustus 1995)</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-[10px] font-bold text-text-secondary uppercase">Golongan Darah</p>
                  <p className="font-bold text-primary text-heading-md mt-0.5">O+</p>
                </div>
                <div>
                  <p className="text-[10px] font-bold text-text-secondary uppercase">Tensi Terakhir</p>
                  <p className="font-bold text-text-primary text-heading-md mt-0.5">120/80</p>
                </div>
              </div>
              <div>
                <p className="text-[10px] font-bold text-text-secondary uppercase">Alergi Terdaftar</p>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  <Badge variant="danger">Debu</Badge>
                  <Badge variant="danger">Kacang Tanah</Badge>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Middle: Chat Interface */}
        <div className="space-y-4">
          <Card className="flex flex-col h-[500px] p-0 overflow-hidden">
            {/* Chat Header */}
            <div className="p-4 bg-primary text-white flex justify-between items-center shrink-0">
              <p className="font-bold text-body-sm">Sesi Chat Konsultasi</p>
              <Badge variant="outline" className="text-white border-white">Sesi Berjalan</Badge>
            </div>

            {/* Message Area */}
            <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-gray-50/50">
              {messages.map((msg, idx) => {
                const isDoc = msg.sender === "doctor";
                return (
                  <div key={idx} className={`flex ${isDoc ? "justify-end" : "justify-start"}`}>
                    <div 
                      className={`max-w-[80%] p-3.5 rounded-2xl text-xs leading-relaxed ${
                        isDoc 
                          ? "bg-primary text-white rounded-tr-none" 
                          : "bg-white text-text-primary rounded-tl-none border border-gray-100 shadow-sm"
                      }`}
                    >
                      <p>{msg.text}</p>
                      <p className={`text-[9px] mt-1 text-right ${isDoc ? "text-white/60" : "text-text-secondary"}`}>{msg.time}</p>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Input Bar */}
            <div className="p-3 border-t border-gray-100 bg-white flex gap-2 shrink-0">
              <input
                type="text"
                placeholder="Tulis pesan medis..."
                className="input-field text-xs py-2 flex-1"
                value={inputMsg}
                onChange={(e) => setInputMsg(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
              />
              <Button onClick={handleSend} size="icon" className="h-[38px] w-[38px] shrink-0">
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </Card>
        </div>

        {/* Right: SOAP Form */}
        <div className="space-y-4">
          <Card className="space-y-4">
            <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3 flex items-center gap-1.5">
              <Clipboard className="w-5 h-5 text-primary" />
              Catatan SOAP Medis
            </h3>

            {submitted ? (
              <div className="p-5 rounded-2xl bg-success-light border border-success/30 text-success text-center space-y-3">
                <Check className="w-10 h-10 text-success mx-auto" />
                <p className="font-bold text-body-sm">Catatan SOAP Berhasil Disimpan</p>
                <p className="text-xs text-text-secondary">Data rekam medis telah ditambahkan ke profil kesehatan Budi Santoso.</p>
              </div>
            ) : (
              <form onSubmit={handleSOAPSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-text-secondary uppercase mb-1.5">Subjective (S)</label>
                  <textarea
                    placeholder="Keluhan subjektif pasien..."
                    className="input-field text-xs min-h-[60px] py-2"
                    value={subjective}
                    onChange={(e) => setSubjective(e.target.value)}
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-text-secondary uppercase mb-1.5">Objective (O)</label>
                  <textarea
                    placeholder="Hasil pemeriksaan fisik/tensi..."
                    className="input-field text-xs min-h-[60px] py-2"
                    value={objective}
                    onChange={(e) => setObjective(e.target.value)}
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-text-secondary uppercase mb-1.5">Assessment (A)</label>
                  <textarea
                    placeholder="Diagnosis ICD-10..."
                    className="input-field text-xs min-h-[60px] py-2"
                    value={assessment}
                    onChange={(e) => setAssessment(e.target.value)}
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-text-secondary uppercase mb-1.5">Plan (P)</label>
                  <textarea
                    placeholder="Rencana resep obat / istirahat..."
                    className="input-field text-xs min-h-[60px] py-2"
                    value={plan}
                    onChange={(e) => setPlan(e.target.value)}
                    required
                  />
                </div>

                <Button type="submit" className="w-full" isLoading={submitting}>
                  Simpan SOAP & Selesaikan
                </Button>
              </form>
            )}
          </Card>
        </div>

      </div>
    </div>
  );
}
