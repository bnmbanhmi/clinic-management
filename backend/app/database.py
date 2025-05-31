from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.context import CryptContext
import enum
import secrets # Add secrets for token generation
from datetime import datetime, timedelta # Add datetime and timedelta
from .config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(str, enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    CLINIC_STAFF = "CLINIC_STAFF"
    ADMIN = "ADMIN"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    # This function ensures that all tables defined in your models are created in the database
    # if they do not already exist. It does not modify existing tables or drop them.
    # For schema changes (like adding new columns to existing tables) after the initial creation,
    # you will need to use a database migration tool like Alembic or apply manual SQL ALTER TABLE commands.
    Base.metadata.create_all(bind=engine, checkfirst=True)