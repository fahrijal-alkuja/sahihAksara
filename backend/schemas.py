from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, List

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    daily_quota: int
    is_active: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserAdminUpdate(BaseModel):
    role: Optional[str] = None
    daily_quota: Optional[int] = None
    is_active: Optional[int] = None

class AdminStats(BaseModel):
    total_users: int
    total_scans: int
    pro_users: int
    scans_today: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Scan Schemas
class ScanBase(BaseModel):
    text_content: str

class ScanCreate(ScanBase):
    pass

class ScanResponse(ScanBase):
    id: int
    user_id: Optional[int] = None
    ai_probability: float
    perplexity: float
    burstiness: float
    status: str
    sentences: list[dict] | None = None
    ai_count: int = 0
    para_count: int = 0
    mix_count: int = 0
    human_count: int = 0
    partially_analyzed: bool = False
    opinion_semantic: Optional[float] = None
    opinion_perplexity: Optional[float] = None
    opinion_burstiness: Optional[float] = None
    opinion_humanity: Optional[float] = None
    citation_percentage: Optional[float] = None
    sha256_hash: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    order_id: str
    amount: float
    plan_type: str
    status: str
    snap_token: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
