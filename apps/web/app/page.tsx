"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Shield, 
  Phone, 
  Clock, 
  FileText, 
  Users, 
  Brain, 
  CheckCircle, 
  ArrowRight,
  Heart,
  Activity,
  AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Logo } from "@/components/shared/logo";
import { Navbar } from "@/components/shared/navbar";

const PRICING_PLANS = [
  {
    name: "Basic (Mandiri)",
    price: "Rp 0",
    period: "/ selamanya",
    desc: "Perlindungan dasar esensial untuk personal.",
    features: [
      "SafePing check-in harian (1x sehari)",
      "MedCard digital dasar & QR code",
      "Maksimum 2 kontak darurat",
      "Akses artikel kesehatan JagaDiri"
    ],
    cta: "Mulai Gratis",
    popular: false,
    color: "primary"
  },
  {
    name: "Standard (JagaDiri)",
    price: "Rp 29.000",
    period: "/ bulan",
    desc: "Perlindungan otomatis & eskalasi lebih cepat.",
    features: [
      "Semua fitur Basic",
      "SafePing terjadwal & fleksibel",
      "Eskalasi otomatis SMS ke 5 kontak darurat",
      "Pemantauan tingkat kepatuhan obat",
      "Simpan rekam medis hingga 50MB"
    ],
    cta: "Pilih Standard",
    popular: true,
    color: "secondary"
  },
  {
    name: "Premium (Lansia Mandiri)",
    price: "Rp 79.000",
    period: "/ bulan",
    desc: "Proteksi penuh plus integrasi layanan medis darurat.",
    features: [
      "Semua fitur Standard",
      "Eskalasi darurat otomatis ke Layanan 119",
      "Prioritas booking konsultasi dokter 24/7",
      "Senior Mode (UI ramah lansia & tulisan besar)",
      "Penyimpanan rekam medis tak terbatas"
    ],
    cta: "Pilih Premium",
    popular: false,
    color: "primary"
  }
];

export default function LandingPage() {
  const TARGET_USERS = 12450;
  const TARGET_DOCTORS = 512;
  const TARGET_PINGS = 99.8;

  const [stats, setStats] = useState({ users: 0, doctors: 0, pings: 0 });

  useEffect(() => {
    let step = 0;
    const totalSteps = 80; // run for 80 * 30ms = 2.4s
    const interval = setInterval(() => {
      step++;
      const progress = Math.min(step / totalSteps, 1);
      // Ease-out: progress^0.5
      const eased = Math.sqrt(progress);
      setStats({
        users: Math.round(TARGET_USERS * eased),
        doctors: Math.round(TARGET_DOCTORS * eased),
        pings: parseFloat((TARGET_PINGS * eased).toFixed(1)),
      });
      if (step >= totalSteps) clearInterval(interval);
    }, 30);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-background flex flex-col selection:bg-primary/20">
      <Navbar />

      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center justify-center pt-24 pb-16 overflow-hidden bg-gradient-to-br from-primary-900 via-primary-800 to-secondary-900 text-white">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(26,107,90,0.15),transparent_60%)]" />
        <div className="container-custom relative z-10 grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-8 text-center md:text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-primary-200">
              <Shield className="w-4 h-4 text-primary-300" />
              <span className="text-sm font-semibold tracking-wider uppercase">Jaring Pengaman Digital No. 1 di Indonesia</span>
            </div>
            <h1 className="text-heading-3xl font-extrabold tracking-tight leading-tight md:text-5xl">
              Selalu Ada yang <span className="text-primary-300 font-heading">Jaga</span>, Walau Tinggal Sendiri.
            </h1>
            <p className="text-body-lg text-white/80 max-w-xl">
              JagaDiri mendeteksi tanda bahaya secara proaktif melalui <strong className="text-primary-300">SafePing</strong> harian dan tombol darurat <strong className="text-danger-light">SOS</strong>. Melindungi Anda, menenangkan keluarga tercinta di mana pun mereka berada.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
              <Link href="/register">
                <Button size="lg" className="w-full sm:w-auto shadow-glow">
                  Daftar Gratis Sekarang <ArrowRight className="w-5 h-5 ml-1" />
                </Button>
              </Link>
              <Link href="/login">
                <Button variant="outline-white" size="lg" className="w-full sm:w-auto">
                  Masuk ke Dashboard
                </Button>
              </Link>
            </div>
          </div>
          <div className="relative flex justify-center">
            {/* Animated UI Mockup Card */}
            <div className="relative w-full max-w-sm p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20 shadow-glass-xl text-white space-y-6">
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
                  <span className="font-semibold text-sm">SafePing Aktif</span>
                </div>
                <span className="text-xs text-white/60">Hari ini 08:00</span>
              </div>
              <div className="text-center py-6">
                <p className="text-white/60 text-sm mb-2">Halo Budi, bagaimana kondisi Anda hari ini?</p>
                <div className="flex justify-center gap-3 mt-4">
                  <span className="w-12 h-12 flex items-center justify-center rounded-xl bg-white/10 hover:bg-primary text-2xl cursor-pointer transition-all">😊</span>
                  <span className="w-12 h-12 flex items-center justify-center rounded-xl bg-white/10 hover:bg-primary text-2xl cursor-pointer transition-all">😐</span>
                  <span className="w-12 h-12 flex items-center justify-center rounded-xl bg-white/10 hover:bg-primary text-2xl cursor-pointer transition-all">🤒</span>
                </div>
              </div>
              <div className="p-4 rounded-xl bg-danger-light/10 border border-danger/30 flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-danger flex items-center justify-center shrink-0">
                  <Phone className="w-5 h-5 text-white animate-bounce" />
                </div>
                <div>
                  <p className="text-xs text-white/60">Aktivasi Darurat</p>
                  <p className="text-sm font-bold text-danger-light">Kirim SOS ke Kontak Terdekat</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Statement */}
      <section className="section-padding bg-surface text-center">
        <div className="container-custom max-w-3xl space-y-6">
          <Heart className="w-12 h-12 mx-auto text-danger animate-pulse" />
          <h2 className="text-heading-2xl text-text-primary">Hidup Mandiri Menyenangkan, Sampai Terjadi Hal yang Tak Terduga.</h2>
          <p className="text-body-lg text-text-secondary">
            Bagi jutaan perantau dan lansia yang tinggal sendiri di Indonesia, risiko medis tanpa pengawasan adalah kenyataan yang nyata. Siapa yang tahu jika Anda jatuh di kamar mandi? Siapa yang membawakan obat saat Anda demam tinggi dan tak mampu berdiri? JagaDiri hadir sebagai jaring pengaman proaktif Anda.
          </p>
        </div>
      </section>

      {/* Features Grid */}
      <section id="fitur" className="section-padding bg-background">
        <div className="container-custom space-y-12">
          <div className="text-center max-w-2xl mx-auto space-y-4">
            <h2 className="text-heading-2xl text-text-primary">6 Pilar Perlindungan Kesehatan JagaDiri</h2>
            <p className="text-text-secondary">Teknologi kesehatan modern yang didesain ramah pengguna untuk kenyamanan hidup mandiri.</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-primary-light text-primary flex items-center justify-center">
                <Clock className="w-6 h-6" />
              </div>
              <h3 className="font-heading font-bold text-heading-md">SafePing Check-in</h3>
              <p className="text-text-secondary text-body-sm">
                Ping otomatis setiap hari pada waktu pilihan Anda. Jika tidak direspons dalam kurun waktu tertentu, keluarga atau layanan darurat langsung dinotifikasi.
              </p>
            </Card>

            <Card className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-danger-light text-danger flex items-center justify-center">
                <Phone className="w-6 h-6" />
              </div>
              <h3 className="font-heading font-bold text-heading-md">SOS Darurat Satu Klik</h3>
              <p className="text-text-secondary text-body-sm">
                Tombol SOS yang mengirimkan SMS darurat berisi lokasi GPS Anda secara akurat ke kontak darurat, serta langsung menghubungi layanan 119.
              </p>
            </Card>

            <Card className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-primary-light text-primary flex items-center justify-center">
                <FileText className="w-6 h-6" />
              </div>
              <h3 className="font-heading font-bold text-heading-md">MedCard & QR Code</h3>
              <p className="text-text-secondary text-body-sm">
                Profil medis darurat berupa QR code untuk layar kunci ponsel Anda. Memudahkan tim medis mengetahui golongan darah, alergi, dan riwayat penting Anda.
              </p>
            </Card>

            <Card className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-secondary-light text-secondary flex items-center justify-center">
                <Clock className="w-6 h-6" />
              </div>
              <h3 className="font-heading font-bold text-heading-md">MedReminder (Pengingat Obat)</h3>
              <p className="text-text-secondary text-body-sm">
                Jadwal dan pengingat minum obat harian untuk Anda. Pantau persentase kepatuhan minum obat mingguan Anda secara rapi.
              </p>
            </Card>

            <Card className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-secondary-light text-secondary flex items-center justify-center">
                <Brain className="w-6 h-6" />
              </div>
              <h3 className="font-heading font-bold text-heading-md">Symptom Checker (AI)</h3>
              <p className="text-text-secondary text-body-sm">
                Periksa gejala pusing, demam, mual secara mandiri. AI kami akan memetakan ke ICD-10 dan memprediksi risiko penyakit dalam hitungan detik.
              </p>
            </Card>

            <Card className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-primary-light text-primary flex items-center justify-center">
                <Users className="w-6 h-6" />
              </div>
              <h3 className="font-heading font-bold text-heading-md">Portal Keluarga & Caregiver</h3>
              <p className="text-text-secondary text-body-sm">
                Bagikan akses pantau status SafePing dan jadwal obat Anda kepada anak, orang tua, atau pasangan jarak jauh secara real-time.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="cara-kerja" className="section-padding bg-surface">
        <div className="container-custom space-y-12">
          <div className="text-center max-w-2xl mx-auto space-y-4">
            <h2 className="text-heading-2xl text-text-primary">Cara Kerja JagaDiri melindungi Anda</h2>
            <p className="text-text-secondary">Hanya butuh 3 langkah mudah untuk mengaktifkan jaring pengaman kesehatan Anda.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 relative">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-primary text-white font-heading font-extrabold text-heading-lg flex items-center justify-center mx-auto shadow-glow">1</div>
              <h3 className="font-bold text-heading-md">Daftar Akun</h3>
              <p className="text-text-secondary text-body-sm">Lengkapi identitas diri, golongan darah, dan kontak darurat yang dapat dipercaya.</p>
            </div>
            <div className="text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-primary text-white font-heading font-extrabold text-heading-lg flex items-center justify-center mx-auto shadow-glow">2</div>
              <h3 className="font-bold text-heading-md">Atur Jadwal SafePing</h3>
              <p className="text-text-secondary text-body-sm">Pilih jam check-in harian (misal: 08:00 pagi). Kami akan mengirimkan notifikasi interaktif tepat waktu.</p>
            </div>
            <div className="text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-primary text-white font-heading font-extrabold text-heading-lg flex items-center justify-center mx-auto shadow-glow">3</div>
              <h3 className="font-bold text-heading-md">Terlindungi 24/7</h3>
              <p className="text-text-secondary text-body-sm">Jika Anda melewati batas waktu check-in, sistem akan menghubungi kontak darurat secara otomatis.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Counter */}
      <section className="section-padding bg-primary text-white text-center">
        <div className="container-custom grid sm:grid-cols-3 gap-8">
          <div className="space-y-2">
            <h3 className="text-4xl font-extrabold text-primary-200">{stats.users.toLocaleString("id-ID")}+</h3>
            <p className="text-sm uppercase tracking-wider text-white/80">Pengguna Aktif</p>
          </div>
          <div className="space-y-2">
            <h3 className="text-4xl font-extrabold text-primary-200">{stats.doctors}+</h3>
            <p className="text-sm uppercase tracking-wider text-white/80">Dokter Terverifikasi</p>
          </div>
          <div className="space-y-2">
            <h3 className="text-4xl font-extrabold text-primary-200">{stats.pings}%</h3>
            <p className="text-sm uppercase tracking-wider text-white/80">Kecepatan Eskalasi</p>
          </div>
        </div>
      </section>

      {/* Pricing Tiers */}
      <section id="harga" className="section-padding bg-background">
        <div className="container-custom space-y-12">
          <div className="text-center max-w-2xl mx-auto space-y-4">
            <h2 className="text-heading-2xl text-text-primary">Investasi Terbaik untuk Ketenangan Anda</h2>
            <p className="text-text-secondary">Pilih perlindungan yang sesuai dengan kebutuhan Anda dan keluarga.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 items-stretch">
            {PRICING_PLANS.map((plan, idx) => (
              <div 
                key={idx}
                className={`relative flex flex-col p-8 rounded-2xl border ${
                  plan.popular 
                    ? "bg-white border-2 border-primary shadow-glass-xl -translate-y-2" 
                    : "bg-surface border-gray-100 shadow-card"
                }`}
              >
                {plan.popular && (
                  <span className="absolute top-0 right-1/2 translate-x-1/2 -translate-y-1/2 bg-primary text-white text-xs font-bold px-4 py-1.5 rounded-full uppercase tracking-wider">
                    Terpopuler
                  </span>
                )}
                <div className="mb-6">
                  <h3 className="font-heading font-bold text-heading-lg text-text-primary">{plan.name}</h3>
                  <p className="text-text-secondary text-body-sm mt-1">{plan.desc}</p>
                </div>
                <div className="mb-8">
                  <span className="text-heading-3xl font-extrabold text-text-primary">{plan.price}</span>
                  <span className="text-text-secondary text-body-sm">{plan.period}</span>
                </div>
                <ul className="space-y-4 mb-8 flex-1">
                  {plan.features.map((feat, fIdx) => (
                    <li key={fIdx} className="flex items-start gap-2.5 text-body-sm text-text-primary">
                      <CheckCircle className="w-5 h-5 text-success shrink-0 mt-0.5" />
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
                <Link href="/register" className="w-full mt-auto">
                  <Button 
                    variant={plan.popular ? "primary" : "outline"} 
                    className="w-full"
                  >
                    {plan.cta}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimoni" className="section-padding bg-surface">
        <div className="container-custom space-y-12">
          <div className="text-center max-w-2xl mx-auto space-y-4">
            <h2 className="text-heading-2xl text-text-primary">Kisah Mereka yang Dijaga</h2>
            <p className="text-text-secondary">Testimoni nyata dari perantau dan anak yang terpisah kota dari orang tua lansia.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-8">
            <Card className="space-y-4">
              <div className="flex gap-1 text-warning">★★★★★</div>
              <p className="italic text-text-primary">
                &ldquo;Saya bekerja di Jakarta sedangkan ibu saya yang lansia tinggal sendiri di Surabaya. Dengan fitur Portal Keluarga JagaDiri, saya bisa memantau apakah Ibu sudah check-in pagi ini dan apakah beliau sudah meminum obat tensinya. JagaDiri memberi saya ketenangan batin yang luar biasa.&rdquo;
              </p>
              <div>
                <p className="font-bold text-text-primary">Rian Prasetyo</p>
                <p className="text-text-secondary text-body-sm">Pekerja IT, Jakarta</p>
              </div>
            </Card>

            <Card className="space-y-4">
              <div className="flex gap-1 text-warning">★★★★★</div>
              <p className="italic text-text-primary">
                &ldquo;Bulan lalu asam lambung saya kambuh parah jam 2 malam di kosan. Sendirian dan tidak kuat jalan. Saya tekan tombol SOS di aplikasi JagaDiri, dan dalam 5 menit teman kos sebelah pintu kamar dikontak sistem dan membawakan saya air hangat dan obat. Jaring pengaman yang sesungguhnya!&rdquo;
              </p>
              <div>
                <p className="font-bold text-text-primary">Annisa Fitriani</p>
                <p className="text-text-secondary text-body-sm">Mahasiswi Perantau, Bandung</p>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Conversion Section */}
      <section
        className="section-padding text-white text-center"
        style={{ background: "linear-gradient(135deg, #040e09 0%, #0B2C24 40%, #0a1a33 100%)" }}
      >
        <div className="container-custom max-w-2xl space-y-8">
          <h2 className="text-heading-2xl font-extrabold">Jangan Tunggu Sampai Darurat Terjadi.</h2>
          <p className="text-white/80">
            Daftarkan diri Anda atau orang tua tercinta hari ini. Mulai dengan gratis dan dapatkan perlindungan kesehatan proaktif 24/7.
          </p>
          <div className="flex justify-center gap-4">
            <Link href="/register">
              <Button size="lg" className="shadow-glow">Daftar Akun Gratis</Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer
        className="text-white border-t border-white/10 py-12"
        style={{ backgroundColor: "#030b06" }}
      >
        <div className="container-custom grid md:grid-cols-4 gap-8">
          <div className="space-y-4">
            <Logo variant="light" />
            <p className="text-xs text-white/60">
              JagaDiri adalah platform jaring pengaman kesehatan digital proaktif pertama di Indonesia. Melindungi solo living di mana saja, kapan saja.
            </p>
          </div>
          <div>
            <h4 className="font-bold text-sm mb-4">Layanan</h4>
            <ul className="space-y-2 text-xs text-white/60">
              <li>SafePing Harian</li>
              <li>SOS Darurat</li>
              <li>MedCard Digital</li>
              <li>E-Konsultasi Dokter</li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold text-sm mb-4">Dukungan</h4>
            <ul className="space-y-2 text-xs text-white/60">
              <li>Hubungi Kami</li>
              <li>Pusat Bantuan</li>
              <li>Kebijakan Privasi</li>
              <li>Syarat &amp; Ketentuan</li>
            </ul>
          </div>
          <div className="space-y-4">
            <h4 className="font-bold text-sm">Keamanan Terjamin</h4>
            <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-xs text-white/60">
              🔒 <strong>UU PDP Compliant</strong>
              <p className="mt-1">Seluruh data rekam medis Anda dienkripsi end-to-end.</p>
            </div>
          </div>
        </div>
        <div className="container-custom border-t border-white/10 mt-8 pt-6 text-center text-xs text-white/40">
          &copy; {new Date().getFullYear()} JagaDiri Indonesia. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
