"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Users, Clock, Star, ArrowRight, UserCheck, MessageSquare, AlertCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function DoctorDashboard() {
  const [loading, setLoading] = useState(true);
  const [queue, setQueue] = useState<any[]>([]);

  useEffect(() => {
    // Simulated Doctor's Patient Queue
    setQueue([
      {
        id: "con-1",
        patient_name: "Budi Santoso",
        type: "chat",
        scheduled_at: new Date().toISOString(),
        chief_complaint: "Pusing hebat di kepala bagian belakang disertai mual",
        is_urgent: false
      },
      {
        id: "con-2",
        patient_name: "Siti Aminah",
        type: "video",
        scheduled_at: new Date(Date.now() + 1800000).toISOString(),
        chief_complaint: "Dada terasa sesak setelah berjalan kaki ringan",
        is_urgent: true
      }
    ]);
    setLoading(false);
  }, []);

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
        <h2 className="text-heading-xl font-bold text-text-primary">👨‍⚕️ Dashboard Praktik Dokter</h2>
        <p className="text-text-secondary text-body-sm mt-1">Pantau antrean konsultasi masuk dan resepkan rekam medis pasien hari ini.</p>
      </div>

      {/* Stats Summary */}
      <div className="grid sm:grid-cols-3 gap-6">
        <Card className="p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-primary-light text-primary flex items-center justify-center">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-bold text-text-secondary uppercase">Antrean Pasien</p>
            <p className="text-heading-lg font-extrabold text-text-primary mt-1">{queue.length} Pasien</p>
          </div>
        </Card>

        <Card className="p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-secondary-light text-secondary flex items-center justify-center">
            <UserCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-bold text-text-secondary uppercase">Selesai Dilayani</p>
            <p className="text-heading-lg font-extrabold text-text-primary mt-1">14 Pasien</p>
          </div>
        </Card>

        <Card className="p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-warning-light text-warning-dark flex items-center justify-center">
            <Star className="w-6 h-6 fill-warning text-warning" />
          </div>
          <div>
            <p className="text-xs font-bold text-text-secondary uppercase">Rating Kepuasan</p>
            <p className="text-heading-lg font-extrabold text-text-primary mt-1">4.9 / 5.0</p>
          </div>
        </Card>
      </div>

      {/* Active Patient Queue */}
      <Card className="space-y-4">
        <h3 className="font-heading font-bold text-heading-md text-text-primary border-b border-gray-100 pb-3">Antrean Konsultasi Hari Ini</h3>
        
        <div className="space-y-4">
          {queue.length > 0 ? (
            queue.map((con) => (
              <div 
                key={con.id} 
                className="p-5 rounded-2xl border border-gray-100 bg-surface flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:shadow-card transition-shadow"
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <p className="font-bold text-text-primary text-body-lg">{con.patient_name}</p>
                    {con.is_urgent && (
                      <Badge variant="urgent" className="text-[10px]">🚨 Gawat Darurat</Badge>
                    )}
                    <Badge variant="outline" className="capitalize">{con.type}</Badge>
                  </div>
                  <p className="text-body-sm text-text-secondary">
                    <strong>Keluhan:</strong> &ldquo;{con.chief_complaint}&rdquo;
                  </p>
                  <p className="text-xs text-text-secondary flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-primary" />
                    Jadwal: {new Date(con.scheduled_at).toLocaleTimeString("id-ID", {
                      hour: "2-digit",
                      minute: "2-digit"
                    })}
                  </p>
                </div>
                
                <div className="w-full md:w-auto shrink-0">
                  <Link href={`/doctor/consultations/${con.id}`}>
                    <Button size="sm" className="w-full md:w-auto flex items-center justify-center">
                      Mulai Konsultasi <ArrowRight className="w-4 h-4 ml-1.5" />
                    </Button>
                  </Link>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-12">
              <AlertCircle className="w-10 h-10 mx-auto text-text-secondary" />
              <p className="text-text-secondary mt-2 text-body-sm font-semibold">Semua antrean pasien hari ini telah diselesaikan.</p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
