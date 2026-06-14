"""
JagaDiri — Layanan Notifikasi (Mock)
Layanan notifikasi yang mencatat ke console untuk pengembangan.
Di produksi, integrasi dengan FCM, SMS (Twilio), dan email.
"""

import logging
from typing import List, Optional
from uuid import UUID

logger = logging.getLogger("jagadiri.notifications")


class NotificationService:
    """Layanan notifikasi mock — semua dikirim ke console log."""

    @staticmethod
    async def send_push(
        user_id: UUID,
        title: str,
        body: str,
        data: Optional[dict] = None,
    ) -> bool:
        """Kirim push notification (mock)."""
        logger.info(
            "📱 PUSH NOTIFICATION | user=%s | title=%s | body=%s | data=%s",
            user_id, title, body, data,
        )
        return True

    @staticmethod
    async def send_sms(
        phone_number: str,
        message: str,
    ) -> bool:
        """Kirim SMS (mock). Di produksi gunakan Twilio."""
        logger.info(
            "📩 SMS | to=%s | message=%s",
            phone_number, message,
        )
        return True

    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        """Kirim email (mock). Di produksi gunakan SendGrid/SES."""
        logger.info(
            "📧 EMAIL | to=%s | subject=%s | body=%s",
            to_email, subject, body[:100],
        )
        return True

    @staticmethod
    async def notify_emergency_contacts(
        user_id: UUID,
        contacts: List[dict],
        event_type: str,
        message: str,
    ) -> List[dict]:
        """Kirim notifikasi ke semua kontak darurat."""
        results = []
        for contact in contacts:
            logger.info(
                "🚨 NOTIFIKASI DARURAT | user=%s | contact=%s | phone=%s | type=%s | msg=%s",
                user_id,
                contact.get("name", "Unknown"),
                contact.get("phone", "Unknown"),
                event_type,
                message,
            )
            results.append({
                "name": contact.get("name"),
                "phone": contact.get("phone"),
                "status": "terkirim",
                "channel": "sms",
            })
        return results

    @staticmethod
    async def notify_119(
        user_id: UUID,
        latitude: Optional[float],
        longitude: Optional[float],
        address: Optional[str],
    ) -> bool:
        """Kirim notifikasi ke 119 (mock)."""
        logger.info(
            "🚑 NOTIFIKASI 119 | user=%s | lat=%s | lng=%s | address=%s",
            user_id, latitude, longitude, address,
        )
        return True

    @staticmethod
    async def send_otp(
        email: str,
        otp_code: str,
    ) -> bool:
        """Kirim OTP ke email (mock)."""
        logger.info(
            "🔐 OTP DIKIRIM | email=%s | kode=%s",
            email, otp_code,
        )
        return True

    @staticmethod
    async def send_safeping_reminder(
        user_id: UUID,
        user_name: str,
    ) -> bool:
        """Kirim pengingat SafePing check-in."""
        logger.info(
            "🔔 SAFEPING REMINDER | user=%s | name=%s | msg=Waktunya check-in! Bagaimana kondisi Anda hari ini?",
            user_id, user_name,
        )
        return True

    @staticmethod
    async def send_medication_reminder(
        user_id: UUID,
        medication_name: str,
        dosage: Optional[str],
    ) -> bool:
        """Kirim pengingat minum obat."""
        dosage_text = f" ({dosage})" if dosage else ""
        logger.info(
            "💊 MEDICATION REMINDER | user=%s | obat=%s%s | msg=Waktunya minum obat!",
            user_id, medication_name, dosage_text,
        )
        return True


# Singleton
notification_service = NotificationService()
