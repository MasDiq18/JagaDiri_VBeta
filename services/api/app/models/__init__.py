"""
JagaDiri — Model Package
Import semua model agar terdeteksi oleh SQLAlchemy/Alembic.
"""

from app.models.user import User, UserMedicalProfile, EmergencyContact, RefreshToken
from app.models.safeping import SafePingConfig, SafePingLog, SOSEvent
from app.models.consultation import Doctor, DoctorSchedule, Consultation, ConsultationNote
from app.models.prescription import Prescription, PrescriptionItem
from app.models.health_record import HealthRecord, VaccinationRecord, VitalSign
from app.models.medication import MedicationOrder, MedicationReminder, MedicationAdherenceLog
from app.models.community import SupportGroup, BuddyPair, BloodDonor
from app.models.gamification import UserGamification, PointTransaction, HealthGoal
from app.models.family import FamilyConnection

__all__ = [
    # User & Auth
    "User",
    "UserMedicalProfile",
    "EmergencyContact",
    "RefreshToken",
    # SafeGuard
    "SafePingConfig",
    "SafePingLog",
    "SOSEvent",
    # Consultation
    "Doctor",
    "DoctorSchedule",
    "Consultation",
    "ConsultationNote",
    # Prescription
    "Prescription",
    "PrescriptionItem",
    # Health Records
    "HealthRecord",
    "VaccinationRecord",
    "VitalSign",
    # Medication
    "MedicationOrder",
    "MedicationReminder",
    "MedicationAdherenceLog",
    # Community
    "SupportGroup",
    "BuddyPair",
    "BloodDonor",
    # Gamification
    "UserGamification",
    "PointTransaction",
    "HealthGoal",
    # Family
    "FamilyConnection",
]
