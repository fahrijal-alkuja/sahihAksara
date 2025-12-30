from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="free") # free, pro, admin
    daily_quota = Column(Integer, default=5)
    pro_expires_at = Column(DateTime, nullable=True) # For Day Pass / Monthly expiry
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    scans = relationship("ScanResult", back_populates="owner")

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Optional for anonymous scans if allowed
    text_content = Column(Text, nullable=False)
    ai_probability = Column(Float, nullable=False)
    perplexity = Column(Float)
    burstiness = Column(Float)
    status = Column(String)
    sentences = Column(JSON, nullable=True)
    # Metadata for Zero-Retention reports
    ai_count = Column(Integer, default=0)
    para_count = Column(Integer, default=0)
    mix_count = Column(Integer, default=0)
    human_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="scans")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    plan_type = Column(String) # 'daily', 'monthly'
    status = Column(String, default="pending") # pending, settlement, expire
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")

class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)
    description = Column(String)
