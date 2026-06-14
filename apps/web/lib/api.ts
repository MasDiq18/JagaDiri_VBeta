/**
 * JagaDiri — API Client & Mock Fallback
 * Menghubungkan frontend Next.js ke FastAPI backend, dengan auto-fallback ke localStorage/mock data jika backend mati.
 */

import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1";

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor request: tambahkan token JWT
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("jagadiri_access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Interceptor response: tangani 401 (token kadaluarsa/invalid)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      // Jangan redirect jika sedang di halaman auth
      const isAuthPage = window.location.pathname.startsWith("/login") ||
                         window.location.pathname.startsWith("/register");
      if (!isAuthPage) {
        localStorage.removeItem("jagadiri_access_token");
        localStorage.removeItem("jagadiri_user");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// Mock database helper using localStorage
const getMockData = (key: string, defaultVal: any) => {
  if (typeof window === "undefined") return defaultVal;
  const val = localStorage.getItem(`jd_mock_${key}`);
  if (!val) {
    localStorage.setItem(`jd_mock_${key}`, JSON.stringify(defaultVal));
    return defaultVal;
  }
  return JSON.parse(val);
};

const setMockData = (key: string, data: any) => {
  if (typeof window !== "undefined") {
    localStorage.setItem(`jd_mock_${key}`, JSON.stringify(data));
  }
};

// Initial Mocks
const INITIAL_DOCTORS = [
  { id: "doc1", full_name: "dr. Rian Pratama", specialization: "Dokter Umum", rating: 4.8, is_online: true, consultation_fee_general: 35000, bio: "Dokter umum yang ramah dan berdedikasi tinggi." },
  { id: "doc2", full_name: "dr. Indah Lestari, Sp.PD", specialization: "Spesialis Penyakit Dalam", rating: 4.9, is_online: true, consultation_fee_general: 80000, bio: "Fokus pada keluhan pencernaan dan penyakit dalam kronis." },
  { id: "doc3", full_name: "dr. Joko Susilo, Sp.KJ", specialization: "Psikiater", rating: 4.7, is_online: false, consultation_fee_general: 90000, bio: "Membantu pasien mengelola stres dan kecemasan." },
  { id: "doc4", full_name: "dr. Fitri Handayani, Sp.OG", specialization: "Obstetri & Ginekologi", rating: 4.9, is_online: true, consultation_fee_general: 95000, bio: "Pendamping kehamilan terpercaya." }
];

const INITIAL_MEDS = [
  { id: "med1", medication_name: "Amlodipine", dosage: "5mg", times_per_day: 1, reminder_times: ["07:00"], with_food: true, start_date: "2026-06-01", is_active: true, notes: "Untuk hipertensi." },
  { id: "med2", medication_name: "Metformin", dosage: "500mg", times_per_day: 2, reminder_times: ["08:00", "20:00"], with_food: true, start_date: "2026-06-01", is_active: true, notes: "Diminum setelah makan." }
];

const INITIAL_VITALS = [
  { id: "v1", metric_type: "blood_pressure", value_systolic: 120, value_diastolic: 80, unit: "mmHg", created_at: new Date().toISOString() },
  { id: "v2", metric_type: "heart_rate", value_numeric: 72, unit: "bpm", created_at: new Date().toISOString() },
  { id: "v3", metric_type: "temperature", value_numeric: 36.5, unit: "°C", created_at: new Date().toISOString() }
];

// Helper to check if API is alive, if not, use mock
export async function safeApiCall<T>(apiCall: () => Promise<T>, mockFallback: () => T): Promise<T> {
  try {
    return await apiCall();
  } catch (err: any) {
    if (err.code === "ERR_NETWORK" || !err.response) {
      console.warn("Backend API tidak merespons. Menggunakan mock local data.");
      return mockFallback();
    }
    throw err;
  }
}

// API Services
export const apiService = {

  // === Status Koneksi ===
  checkBackendStatus: async (): Promise<{ api: boolean; database: string; latency_ms: number | null }> => {
    try {
      const start = Date.now();
      const res = await api.get("/health", { timeout: 3000 });
      const latency_ms = Date.now() - start;
      return {
        api: true,
        database: res.data?.database || "unknown",
        latency_ms,
      };
    } catch {
      return { api: false, database: "disconnected", latency_ms: null };
    }
  },

  // Authentication

  login: async (email: string, pass: string) => {
    return safeApiCall(
      async () => {
        const res = await api.post("/auth/login", { email, password: pass });
        localStorage.setItem("jagadiri_access_token", res.data.token.access_token);
        localStorage.setItem("jagadiri_user", JSON.stringify(res.data.user));
        return res.data;
      },
      () => {
        // Mock login
        const mockUser = {
          id: "usr-mock-123",
          email,
          full_name: email.includes("budi") ? "Budi Santoso" : email.includes("siti") ? "Siti Aminah" : "Pengguna JagaDiri",
          is_verified: true,
          subscription_tier: email.includes("siti") ? "gold" : "basic"
        };
        localStorage.setItem("jagadiri_access_token", "mock-jwt-token");
        localStorage.setItem("jagadiri_user", JSON.stringify(mockUser));
        return { user: mockUser, pesan: "Login berhasil (Mock)" };
      }
    );
  },

  register: async (data: any) => {
    return safeApiCall(
      async () => {
        const res = await api.post("/auth/register", data);
        return res.data;
      },
      () => {
        return { id: "mock-id-new", full_name: data.full_name, email: data.email, onboarding_completed: true };
      }
    );
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("jagadiri_access_token");
      localStorage.removeItem("jagadiri_user");
    }
  },

  getCurrentUser: () => {
    if (typeof window === "undefined") return null;
    const user = localStorage.getItem("jagadiri_user");
    return user ? JSON.parse(user) : null;
  },

  // SafePing
  getSafePingConfig: async () => {
    const user = apiService.getCurrentUser();
    return safeApiCall(
      async () => (await api.get("/safeping/config")).data,
      () => getMockData("safeping_config", { is_enabled: true, check_in_time: "08:00", response_window_minutes: 120, escalation_to_emergency_contacts: true, escalation_to_119: false })
    );
  },

  updateSafePingConfig: async (config: any) => {
    return safeApiCall(
      async () => (await api.put("/safeping/config", config)).data,
      () => {
        const current = getMockData("safeping_config", {});
        const updated = { ...current, ...config };
        setMockData("safeping_config", updated);
        return updated;
      }
    );
  },

  checkIn: async (moodScore: number, note: string) => {
    return safeApiCall(
      async () => (await api.post("/safeping/checkin", { mood_score: moodScore, quick_note: note })).data,
      () => {
        const history = getMockData("checkin_history", []);
        const newLog = {
          id: `log-${Date.now()}`,
          scheduled_at: new Date().toISOString(),
          responded_at: new Date().toISOString(),
          status: "responded",
          mood_score: moodScore,
          quick_note: note
        };
        history.unshift(newLog);
        setMockData("checkin_history", history);
        return newLog;
      }
    );
  },

  getCheckInHistory: async () => {
    return safeApiCall(
      async () => (await api.get("/safeping/checkin/history")).data,
      () => getMockData("checkin_history", [
        { id: "log-1", scheduled_at: new Date(Date.now() - 86400000).toISOString(), responded_at: new Date(Date.now() - 86400000).toISOString(), status: "responded", mood_score: 4, quick_note: "Hari yang produktif" },
        { id: "log-2", scheduled_at: new Date(Date.now() - 172800000).toISOString(), responded_at: new Date(Date.now() - 172800000).toISOString(), status: "responded", mood_score: 5, quick_note: "Merasa sangat bugar" }
      ])
    );
  },

  triggerSOS: async (lat?: number, lng?: number, addr?: string) => {
    return safeApiCall(
      async () => (await api.post("/safeping/sos", { latitude: lat, longitude: lng, address_snapshot: addr })).data,
      () => {
        const events = getMockData("sos_history", []);
        const newEvent = {
          id: `sos-${Date.now()}`,
          triggered_at: new Date().toISOString(),
          latitude: lat || -6.2088,
          longitude: lng || 106.8456,
          address_snapshot: addr || "Jl. Sudirman No. 21, Jakarta Pusat",
          status: "active",
          service_119_notified: false
        };
        events.unshift(newEvent);
        setMockData("sos_history", events);
        return newEvent;
      }
    );
  },

  getSOSHistory: async () => {
    return safeApiCall(
      async () => (await api.get("/safeping/sos/history")).data,
      () => getMockData("sos_history", [])
    );
  },

  // Doctors & Booking
  getDoctors: async () => {
    return safeApiCall(
      async () => (await api.get("/consultations/doctors")).data.doctors,
      () => getMockData("doctors", INITIAL_DOCTORS)
    );
  },

  bookConsultation: async (doctorVal: any) => {
    return safeApiCall(
      async () => (await api.post("/consultations/booking", doctorVal)).data,
      () => {
        const consults = getMockData("consultations", []);
        const doctor = getMockData("doctors", INITIAL_DOCTORS).find((d: any) => d.id === doctorVal.doctor_id);
        const newConsult = {
          id: `con-${Date.now()}`,
          patient_id: "usr-mock-123",
          doctor_id: doctorVal.doctor_id,
          doctor_name: doctor?.full_name || "dr. Rian Pratama",
          specialization: doctor?.specialization || "Dokter Umum",
          type: doctorVal.type,
          status: "confirmed",
          scheduled_at: doctorVal.scheduled_at || new Date(Date.now() + 3600000).toISOString(),
          chief_complaint: doctorVal.chief_complaint,
          patient_notes: doctorVal.patient_notes,
          is_urgent: doctorVal.is_urgent,
          agora_channel_name: "mock-channel-id",
          fee_charged: doctor?.consultation_fee_general || 35000,
          payment_status: "paid",
          created_at: new Date().toISOString()
        };
        consults.unshift(newConsult);
        setMockData("consultations", consults);
        return newConsult;
      }
    );
  },

  getConsultations: async () => {
    return safeApiCall(
      async () => (await api.get("/consultations/history")).data,
      () => getMockData("consultations", [])
    );
  },

  // MedCard
  getMedCard: async () => {
    return safeApiCall(
      async () => (await api.get("/users/me/medcard")).data,
      () => {
        const user = apiService.getCurrentUser() || { full_name: "Budi Santoso", date_of_birth: "1995-08-17", gender: "male" };
        const config = getMockData("safeping_config", {});
        return {
          user_id: user.id || "usr-mock-123",
          full_name: user.full_name,
          date_of_birth: user.date_of_birth,
          gender: user.gender,
          blood_type: "AB+",
          allergies: ["Kucing", "Penisilin"],
          chronic_conditions: ["Asma"],
          current_medications: ["Salbutamol Inhaler (bila perlu)"],
          emergency_contact_name: "Rudi Santoso",
          emergency_contact_phone: "+6281299998888",
          emergency_contact_relation: "Kakak Kandung",
          bpjs_number: "0001888277382",
          insurance_provider: "BPJS Kesehatan",
          qr_code_url: `https://api.jagadiri.id/v1/users/medcard/${user.id || 'usr-mock-123'}/public`
        };
      }
    );
  },

  // Med Reminders
  getReminders: async () => {
    return safeApiCall(
      async () => (await api.get("/medications/reminders")).data,
      () => getMockData("med_reminders", INITIAL_MEDS)
    );
  },

  createReminder: async (remData: any) => {
    return safeApiCall(
      async () => (await api.post("/medications/reminders", remData)).data,
      () => {
        const meds = getMockData("med_reminders", INITIAL_MEDS);
        const newRem = {
          id: `med-${Date.now()}`,
          user_id: "usr-mock-123",
          medication_name: remData.medication_name,
          dosage: remData.dosage,
          times_per_day: remData.times_per_day,
          reminder_times: remData.reminder_times,
          with_food: remData.with_food,
          start_date: remData.start_date,
          end_date: remData.end_date,
          is_active: true,
          notes: remData.notes,
          created_at: new Date().toISOString()
        };
        meds.push(newRem);
        setMockData("med_reminders", meds);
        return newRem;
      }
    );
  },

  markMedTaken: async (reminderId: string, notes?: string) => {
    return safeApiCall(
      async () => (await api.post(`/medications/reminders/${reminderId}/take`, { notes })).data,
      () => {
        const history = getMockData("med_adherence_log", []);
        const newLog = {
          id: `log-${Date.now()}`,
          reminder_id: reminderId,
          scheduled_at: new Date().toISOString(),
          taken_at: new Date().toISOString(),
          status: "taken",
          notes
        };
        history.unshift(newLog);
        setMockData("med_adherence_log", history);
        return newLog;
      }
    );
  },

  getMedAdherenceReport: async () => {
    return safeApiCall(
      async () => (await api.get("/medications/report")).data,
      () => {
        const meds = getMockData("med_reminders", INITIAL_MEDS);
        const detail = meds.map((m: any) => ({
          reminder_id: m.id,
          medication_name: m.medication_name,
          total_jadwal: 15,
          total_diminum: 14,
          persentase: 93.3
        }));
        return {
          user_id: "usr-mock-123",
          periode_awal: "2026-05-09",
          periode_akhir: "2026-06-09",
          total_jadwal: 30,
          total_diminum: 28,
          total_dilewati: 2,
          total_terlambat: 0,
          persentase_kepatuhan: 93.3,
          detail_per_obat: detail
        };
      }
    );
  },

  // Health Vitals
  getVitals: async () => {
    return safeApiCall(
      async () => (await api.get("/health-records/vitals")).data,
      () => getMockData("vital_signs", INITIAL_VITALS)
    );
  },

  addVital: async (vitalData: any) => {
    return safeApiCall(
      async () => (await api.post("/health-records/vitals", vitalData)).data,
      () => {
        const vitals = getMockData("vital_signs", INITIAL_VITALS);
        const newVital = {
          id: `v-${Date.now()}`,
          user_id: "usr-mock-123",
          metric_type: vitalData.metric_type,
          value_numeric: vitalData.value_numeric,
          value_systolic: vitalData.value_systolic,
          value_diastolic: vitalData.value_diastolic,
          unit: vitalData.unit || "N/A",
          source: vitalData.source || "manual",
          notes: vitalData.notes,
          created_at: new Date().toISOString()
        };
        vitals.unshift(newVital);
        setMockData("vital_signs", vitals);
        return newVital;
      }
    );
  },

  // Symptom Checker (AI)
  checkSymptoms: async (symptoms: string[]) => {
    return safeApiCall(
      async () => (await api.post("/ai/symptom-check", { gejala: symptoms })).data,
      () => {
        const sym = symptoms.map(s => s.toLowerCase());
        let conditions: any[] = [];
        let urgensi = "rendah";
        let saran = "Istirahat cukup dan pantau kondisi Anda.";

        if (sym.some(s => s.includes("dada") || s.includes("nafas") || s.includes("napas"))) {
          urgensi = "darurat";
          saran = "SEGERA HUBUNGI IGD 119 ATAU KE RUMAH SAKIT TERDEKAT!";
          conditions.push({
            nama_kondisi: "Kecurigaan Sindrom Koroner Akut",
            nama_kondisi_medis: "Suspect Acute Coronary Syndrome",
            kode_icd10: "I21.9",
            probabilitas: "sedang",
            penjelasan: "Penyumbatan mendadak pada aliran darah arteri jantung.",
            saran_tindakan: "Minta tolong tetangga, jangan mengemudi sendiri, segera ke UGD."
          });
        } else if (sym.some(s => s.includes("demam") || s.includes("panas"))) {
          urgensi = "sedang";
          saran = "Minum obat penurun panas dan pantau suhu tubuh.";
          conditions.push({
            nama_kondisi: "Demam Berdarah Dengue (DBD)",
            nama_kondisi_medis: "Dengue Fever",
            kode_icd10: "A90",
            probabilitas: "sedang",
            penjelasan: "Demam akibat gigitan nyamuk Aedes aegypti.",
            saran_tindakan: "Lakukan tes darah jika demam berlanjut lebih dari 3 hari."
          });
        } else {
          conditions.push({
            nama_kondisi: "Kelelahan / Masuk Angin",
            nama_kondisi_medis: "Malaise & Fatigue",
            kode_icd10: "R53.83",
            probabilitas: "tinggi",
            penjelasan: "Tubuh kekurangan daya tahan akibat kelelahan.",
            saran_tindakan: "Tidur cukup, minum vitamin, makan hangat."
          });
        }

        return {
          gejala_dianalisis: symptoms,
          gejala_tidak_dikenal: [],
          kondisi_mungkin: conditions,
          tingkat_urgensi: urgensi,
          saran_umum: saran,
          disclaimer: "⚠️ PENTING: Analisis ini adalah simulasi sistem aturan mandiri JagaDiri dan tidak menggantikan anjuran dokter asli."
        };
      }
    );
  },

  getHealthInsights: async () => {
    return safeApiCall(
      async () => (await api.get("/ai/health-insights")).data,
      () => {
        return {
          user_id: "usr-mock-123",
          ringkasan_kesehatan: "Kondisi Anda terpantau stabil berdasarkan data terakhir. Kepatuhan minum obat Anda sangat baik (93.3%).",
          saran_kesehatan: [
            "Lakukan aktivitas fisik ringan seperti jalan sehat di pagi hari.",
            "Pastikan Anda meminum Amledopine sesuai alarm jam 07:00."
          ],
          pengingat: ["Jadwal tensi darah berikutnya: Besok Pagi."],
          skor_kesehatan: 85,
          disclaimer: "Wawasan ini dihasilkan secara otomatis oleh sistem JagaDiri."
        };
      }
    );
  },

  // Family Portal
  getFamilyConnections: async () => {
    return safeApiCall(
      async () => (await api.get("/family/connections")).data,
      () => getMockData("family_connections", [])
    );
  },

  inviteFamilyMember: async (inviteData: any) => {
    return safeApiCall(
      async () => (await api.post("/family/invite", inviteData)).data,
      () => {
        const conns = getMockData("family_connections", []);
        const newConn = {
          id: `conn-${Date.now()}`,
          user_id: "usr-mock-123",
          family_member_id: `fam-${Date.now()}`,
          family_member_name: inviteData.email.split("@")[0].toUpperCase(),
          relation: inviteData.relation,
          access_level: inviteData.access_level,
          can_view_safeping: inviteData.can_view_safeping,
          can_view_medication_adherence: inviteData.can_view_medication_adherence,
          can_view_vital_signs: inviteData.can_view_vital_signs,
          can_view_consultation_history: inviteData.can_view_consultation_history,
          can_view_mental_health: inviteData.can_view_mental_health,
          status: "pending",
          created_at: new Date().toISOString()
        };
        conns.push(newConn);
        setMockData("family_connections", conns);
        return newConn;
      }
    );
  },

  // === Profil Medis ===
  updateMedProfile: async (data: any) => {
    return safeApiCall(
      async () => (await api.put("/users/me/medical-profile", data)).data,
      () => {
        const current = getMockData("med_profile", {});
        const updated = { ...current, ...data };
        setMockData("med_profile", updated);
        return updated;
      }
    );
  },

  getMedProfile: async () => {
    return safeApiCall(
      async () => (await api.get("/users/me/medical-profile")).data,
      () => getMockData("med_profile", {
        blood_type: "O+",
        allergies: [],
        chronic_conditions: [],
        current_medications: [],
        bpjs_number: null,
        insurance_provider: null,
      })
    );
  },

  // === Kontak Darurat ===
  addEmergencyContact: async (contactData: any) => {
    return safeApiCall(
      async () => (await api.post("/users/me/emergency-contacts", contactData)).data,
      () => {
        const contacts = getMockData("emergency_contacts", []);
        const newContact = {
          id: `ec-${Date.now()}`,
          user_id: "usr-mock-123",
          name: contactData.name,
          phone: contactData.phone,
          relation: contactData.relation || "Keluarga",
          priority: contactData.priority || 1,
          can_view_health_status: false,
          can_view_medications: false,
          can_view_consultation_history: false,
          is_active: true,
        };
        contacts.push(newContact);
        setMockData("emergency_contacts", contacts);
        return newContact;
      }
    );
  },

  getEmergencyContacts: async () => {
    return safeApiCall(
      async () => (await api.get("/users/me/emergency-contacts")).data,
      () => getMockData("emergency_contacts", [])
    );
  },

  updateProfile: async (data: any) => {
    return safeApiCall(
      async () => (await api.put("/users/me", data)).data,
      () => {
        const user = apiService.getCurrentUser() || {};
        const updated = { ...user, ...data };
        if (typeof window !== "undefined") {
          localStorage.setItem("jagadiri_user", JSON.stringify(updated));
        }
        return updated;
      }
    );
  },
};
