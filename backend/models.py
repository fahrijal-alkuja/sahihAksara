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
    is_active = Column(Integer, default=1) # 1 for active, 0 for restricted (using Integer for SQLite compatibility or just to be safe)
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
    opinion_semantic = Column(Float, nullable=True)
    opinion_perplexity = Column(Float, nullable=True)
    opinion_burstiness = Column(Float, nullable=True)
    opinion_humanity = Column(Float, nullable=True)
    sha256_hash = Column(String, nullable=True) # Digital Fingerprint for Certificate
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
    snap_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")

class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)
    description = Column(String)
