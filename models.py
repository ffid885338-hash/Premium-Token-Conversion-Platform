import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base

class ConversionStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class TokenType(str, enum.Enum):
    EAT_TO_ACCESS = "EAT_TO_ACCESS"
    ACCESS_TO_JWT = "ACCESS_TO_JWT"
    EAT_TO_JWT = "EAT_TO_JWT"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    oauth_provider = Column(String(50), nullable=False) # google, facebook, vk, apple, x
    oauth_id = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=True)
    username = Column(String(100), nullable=False)
    telegram_username = Column(String(100), nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversions = relationship("ConversionLog", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user")

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String(64), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=60) # requests per minute
    total_calls = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="api_keys")

class ConversionLog(Base):
    __tablename__ = "conversion_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    telegram_username = Column(String(100), nullable=True)
    conversion_type = Column(Enum(TokenType), nullable=False)
    input_token_hash = Column(String(64), nullable=False) # SHA256 of input token for safety
    result_token_hint = Column(String(32), nullable=False) # Last 6 characters only for security
    status = Column(Enum(ConversionStatus), default=ConversionStatus.PENDING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="conversions")

class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)