"""
Database models for user authentication and data storage.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    equation_tabs = relationship("EquationTab", back_populates="user", cascade="all, delete-orphan")
    registration_token = relationship("RegistrationToken", back_populates="user", uselist=False)


class UserPreferences(Base):
    """User preferences for theme, colors, and other settings."""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    theme_mode = Column(String(10), default="dark")  # 'light' or 'dark'
    accent_hue = Column(Integer, default=25)
    accent_brightness = Column(Integer, default=40)
    # Flexible JSON field for future settings
    extra_settings = Column(JSON, default=dict)

    user = relationship("User", back_populates="preferences")


class EquationTab(Base):
    """A custom equation tab containing multiple equation sets."""
    __tablename__ = "equation_tabs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tab_id = Column(String(100), nullable=False)  # Frontend-generated ID
    name = Column(String(100), nullable=False, default="My Equations")
    icon = Column(String(10), default="📐")
    position = Column(Integer, default=0)  # For ordering tabs
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="equation_tabs")
    equation_sets = relationship("EquationSet", back_populates="tab", cascade="all, delete-orphan")


class EquationSet(Base):
    """A single equation set (mini-editor) within a tab."""
    __tablename__ = "equation_sets"

    id = Column(Integer, primary_key=True, index=True)
    tab_id = Column(Integer, ForeignKey("equation_tabs.id", ondelete="CASCADE"), nullable=False)
    set_id = Column(String(100), nullable=False)  # Frontend-generated ID
    title = Column(String(200), nullable=False, default="New Equation Set")
    description = Column(Text, default="")
    equations = Column(Text, default="")  # The actual equation text
    position = Column(Integer, default=0)  # For ordering within tab

    tab = relationship("EquationTab", back_populates="equation_sets")


class RegistrationToken(Base):
    """Registration tokens for limiting user signup."""
    __tablename__ = "registration_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(20), unique=True, nullable=False, index=True)
    used_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    used_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="registration_token")


# List of valid registration tokens
VALID_TOKENS = [
    "ENG-7K2M9-XP4NQ",
    "ENG-3H8Y6-RW2JL",
    "ENG-9F5D1-BT7ZC",
    "ENG-2L4G8-MN6VX",
    "ENG-6Q1W5-KJ3HP",
    "ENG-8C9E2-YS4DF",
    "ENG-4R7T0-UX1BN",
    "ENG-5N3A6-ZQ8GM",
    "ENG-1V2P4-HC9WL",
    "ENG-0B6J7-FR5YK",
]
