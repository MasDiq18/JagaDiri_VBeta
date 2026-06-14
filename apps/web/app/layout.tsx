import type { Metadata, Viewport } from "next";
import { Inter, Plus_Jakarta_Sans } from "next/font/google";
import { Providers } from "@/lib/providers";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-plus-jakarta",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "JagaDiri — Selalu Ada yang Jaga",
    template: "%s | JagaDiri",
  },
  description:
    "Platform kesehatan digital untuk warga Indonesia yang tinggal sendiri. SafePing, konsultasi dokter online, pengingat obat, dan MedCard darurat — semua dalam satu aplikasi.",
  keywords: [
    "kesehatan digital",
    "tinggal sendiri",
    "SafePing",
    "konsultasi dokter online",
    "pengingat obat",
    "MedCard darurat",
    "telemedicine Indonesia",
    "JagaDiri",
  ],
  authors: [{ name: "JagaDiri" }],
  openGraph: {
    title: "JagaDiri — Selalu Ada yang Jaga",
    description:
      "Platform kesehatan digital untuk warga Indonesia yang tinggal sendiri. Perlindungan kesehatan 24/7.",
    type: "website",
    locale: "id_ID",
    siteName: "JagaDiri",
  },
  twitter: {
    card: "summary_large_image",
    title: "JagaDiri — Selalu Ada yang Jaga",
    description:
      "Platform kesehatan digital untuk warga Indonesia yang tinggal sendiri.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  themeColor: "#1A6B5A",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id" className={`${inter.variable} ${plusJakarta.variable}`}>
      <body className="antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
