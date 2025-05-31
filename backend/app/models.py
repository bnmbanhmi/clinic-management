from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, Date, Text, DateTime, ForeignKey # Add Date, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship # Add relationship
from sqlalchemy.ext.hybrid import hybrid_property # Add hybrid_property
from .database import Base, UserRole # Import Base and UserRole from database.py
from datetime import datetime # Add datetime
from typing import Optional # Added Optional for type hinting

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.PATIENT) 
    full_name = Column(String, nullable=True)
    reset_password_token = Column(String, nullable=True, index=True, unique=True) # Added for password reset
    reset_password_token_expires_at = Column(DateTime, nullable=True) # Added for password reset
    # Add other relevant fields for User

    __table_args__ = {'extend_existing': True}

    # Relationships
    # If a user is a patient, this links to their patient record
    patient_profile = relationship("Patient", uselist=False, foreign_keys="Patient.user_id", back_populates="user", cascade="all, delete-orphan") # Will be updated below
    
    created_patients = relationship("Patient", foreign_keys="Patient.creator_id", back_populates="creator") # Will be updated
    # Renamed from assigned_patients_as_doctor for consistency
    assigned_patients = relationship("Patient", foreign_keys="Patient.assigned_doctor_id", back_populates="assigned_doctor") # Will be updated

    # Relationships for appointments
    created_appointments = relationship("Appointment", foreign_keys="Appointment.created_by_user_id", back_populates="created_by_user") # Will be updated
    doctor_appointments = relationship("Appointment", foreign_keys="Appointment.doctor_id", back_populates="doctor") # Will be updated
    # Removed User.patient_appointments relationship

    # Relationships for chat messages
    chat_messages = relationship("ChatMessage", back_populates="user") # Will be updated

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    medical_history = Column(Text, nullable=True)
    emr_summary = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True) 
    assigned_doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships will be updated below to use direct class references
    user = relationship("User", foreign_keys=[user_id], back_populates="patient_profile")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_patients")
    assigned_doctor = relationship("User", foreign_keys=[assigned_doctor_id], back_populates="assigned_patients")
    appointments = relationship("Appointment", back_populates="patient") # Will be updated

    @hybrid_property
    def full_name(self):
        if self.user:
            return self.user.full_name
        return None

    __table_args__ = {'extend_existing': True}

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String, default="Scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships will be updated below
    patient = relationship(Patient, foreign_keys=[patient_id], back_populates="appointments")
    doctor = relationship(User, foreign_keys=[doctor_id], back_populates="doctor_appointments")
    created_by_user = relationship(User, foreign_keys=[created_by_user_id], back_populates="created_appointments")

    __table_args__ = {'extend_existing': True}

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship will be updated below
    user = relationship(User, foreign_keys=[user_id], back_populates="chat_messages")

    __table_args__ = {'extend_existing': True}

# Update relationships in User to use direct class references and correct foreign_keys
User.patient_profile = relationship(Patient, uselist=False, foreign_keys=[Patient.user_id], back_populates="user", cascade="all, delete-orphan")
User.created_patients = relationship(Patient, foreign_keys=[Patient.creator_id], back_populates="creator")
User.assigned_patients = relationship(Patient, foreign_keys=[Patient.assigned_doctor_id], back_populates="assigned_doctor")
User.created_appointments = relationship(Appointment, foreign_keys=[Appointment.created_by_user_id], back_populates="created_by_user")
User.doctor_appointments = relationship(Appointment, foreign_keys=[Appointment.doctor_id], back_populates="doctor")
User.chat_messages = relationship(ChatMessage, foreign_keys=[ChatMessage.user_id], back_populates="user")

# Update relationships in Patient
Patient.appointments = relationship(Appointment, foreign_keys=[Appointment.patient_id], back_populates="patient")