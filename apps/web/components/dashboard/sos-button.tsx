"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Phone, X, AlertTriangle, Loader2, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { apiService } from "@/lib/api";

export function SOSButton() {
  const [showConfirm, setShowConfirm] = useState(false);
  const [activated, setActivated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);

  const handleSOS = async () => {
    setLoading(true);
    setError(null);

    const triggerSOS = async (lat: number, lng: number, address: string) => {
      try {
        await apiService.triggerSOS(lat, lng, address);
        setActivated(true);
        setShowConfirm(false);
        // Auto-dismiss after 8 seconds
        setTimeout(() => setActivated(false), 8000);
      } catch (err: any) {
        setError("Gagal mengirim SOS. Hubungi 119 secara langsung.");
      } finally {
        setLoading(false);
      }
    };

    // Dapatkan lokasi GPS pengguna
    if (typeof navigator !== "undefined" && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          const lat = pos.coords.latitude;
          const lng = pos.coords.longitude;
          setLocation({ lat, lng });
          await triggerSOS(lat, lng, `Koordinat GPS: ${lat.toFixed(6)}, ${lng.toFixed(6)}`);
        },
        async () => {
          // Izin lokasi ditolak — tetap kirim SOS tanpa koordinat
          await triggerSOS(0, 0, "Lokasi tidak tersedia (izin GPS ditolak)");
        },
        { timeout: 5000, maximumAge: 60000 }
      );
    } else {
      // Browser tidak mendukung geolocation
      await triggerSOS(0, 0, "Lokasi tidak tersedia");
    }
  };

  return (
    <>
      {/* SOS Floating Button */}
      <motion.button
        id="sos-button"
        onClick={() => { setError(null); setShowConfirm(true); }}
        className="sos-button"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        aria-label="Tombol Darurat SOS"
      >
        <Phone className="w-7 h-7" />
      </motion.button>

      {/* Confirmation Modal */}
      <Modal
        isOpen={showConfirm}
        onClose={() => setShowConfirm(false)}
        size="sm"
      >
        <div className="text-center py-4">
          <div className="w-20 h-20 rounded-full bg-danger-light mx-auto flex items-center justify-center mb-4">
            <AlertTriangle className="w-10 h-10 text-danger" />
          </div>
          <h3 className="font-heading font-bold text-heading-md text-text-primary mb-2">
            Aktivasi Darurat?
          </h3>
          <p className="text-text-secondary mb-2">
            Tindakan ini akan mengirimkan notifikasi darurat ke semua kontak darurat Anda
            beserta lokasi terkini.
          </p>
          {/* Info lokasi */}
          <div className="flex items-center justify-center gap-1 text-xs text-text-muted mb-4">
            <MapPin className="w-3 h-3" />
            <span>Lokasi GPS akan otomatis disertakan</span>
          </div>
          {/* Error message */}
          {error && (
            <div className="bg-danger/10 border border-danger/30 text-danger text-sm p-3 rounded-xl mb-4">
              {error}
            </div>
          )}
          <div className="flex gap-3">
            <Button
              variant="ghost"
              className="flex-1"
              onClick={() => setShowConfirm(false)}
              id="sos-cancel"
              disabled={loading}
            >
              Batal
            </Button>
            <Button
              variant="danger"
              className="flex-1"
              onClick={handleSOS}
              id="sos-confirm"
              disabled={loading}
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Phone className="w-5 h-5" />
              )}
              {loading ? "Mengirim..." : "Kirim SOS"}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Activated Overlay */}
      <AnimatePresence>
        {activated && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[200] bg-danger/95 flex items-center justify-center"
          >
            <div className="text-center text-white px-6">
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 1 }}
                className="w-24 h-24 rounded-full bg-white/20 mx-auto flex items-center justify-center mb-6"
              >
                <Phone className="w-12 h-12" />
              </motion.div>
              <h2 className="font-heading font-bold text-3xl mb-2">
                SOS Terkirim!
              </h2>
              <p className="text-white/80 text-lg mb-2">
                Kontak darurat Anda telah diberitahu
              </p>
              {location && (
                <p className="text-white/60 text-sm mb-8">
                  Koordinat: {location.lat.toFixed(5)}, {location.lng.toFixed(5)}
                </p>
              )}
              {!location && (
                <p className="text-white/60 text-sm mb-8">
                  Tanpa koordinat GPS
                </p>
              )}
              <Button
                variant="outline-white"
                onClick={() => setActivated(false)}
              >
                <X className="w-5 h-5" />
                Tutup
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
