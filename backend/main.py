from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import uvicorn
import io
import models
import schemas
import database
from core.ai_detector import AIDetector
from core.doc_processor import DocumentProcessor
from core.report_generator import ReportGenerator
from core.auth import get_password_hash, verify_password, create_access_token, get_current_user, get_current_admin_user
from core.maintenance import purge_sensitive_data, delete_user_history, expire_old_history
from core.middleware import PrivacyShieldMiddleware, setup_privacy_logging
from fastapi import BackgroundTasks
from sqlalchemy import func
import os
import requests
import uuid
import hmac
import hashlib
import logging
from fastapi import Request
from dotenv import load_dotenv
import datetime
from datetime import timedelta

load_dotenv()

UNIKAPAY_API_KEY = os.getenv("UNIKAPAY_API_KEY")
UNIKAPAY_BASE_URL = os.getenv("UNIKAPAY_BASE_URL")

# Initialize database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="SahihAksara API", description="API for Indonesian AI Content Detection")

# --- PRIVACY SHIELD ---
app.add_middleware(PrivacyShieldMiddleware)

@app.on_event("startup")
async def startup_event():
    setup_privacy_logging()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the internal error safely (IPs will be masked by formatter)
    logging.error(f"Internal Server Error: {str(exc)}")
    return Response(
        content='{"detail": "Terjadi kesalahan internal pada server. Silakan hubungi admin jika masalah berlanjut."}',
        status_code=500,
        media_type="application/json"
    )

# --- AUTH ENDPOINTS ---

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar.")
    
    hashed_pwd = get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pwd,
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# --- SERVICES ---
detector = AIDetector()
doc_processor = DocumentProcessor()
report_gen = ReportGenerator()

# Setup CORS for Nuxt.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to SahihAksara API", "version": "0.1.0"}

@app.post("/analyze", response_model=schemas.ScanResponse)
async def analyze_text(
    request: schemas.ScanCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Freemium Logic: Check Word Count
    words = request.text_content.split()
    word_count = len(words)
    
    if current_user.role == "free":
        if word_count > 800:
            raise HTTPException(
                status_code=403, 
                detail=f"Batas gratis 800 kata terlampaui (Anda mencoba: {word_count} kata). Silakan upgrade ke Pro!"
            )
        # Check Quota
        if current_user.daily_quota <= 0:
            raise HTTPException(
                status_code=403, 
                detail="Kuota harian gratis Anda sudah habis. Silakan balik lagi besok atau upgrade ke Pro!"
            )
    
    # 2. Analyze (Pro/Admin bypass Hybrid Sampling)
    force_full = current_user.role in ["pro", "admin"]
    result = detector.analyze(request.text_content, force_full_scan=force_full)
    
    # 3. Deduct Quota for Free Users
    if current_user.role == "free":
        current_user.daily_quota -= 1
    
    # 4. Save to database (Metadata persistent, sentences kept briefly)
    sentences = result.get("sentences", [])
    ai_c = sum(1 for s in sentences if s.get("score", 0) > 70)
    para_c = sum(1 for s in sentences if 40 < s.get("score", 0) <= 70)
    mix_c = sum(1 for s in sentences if 15 < s.get("score", 0) <= 40)
    human_c = sum(1 for s in sentences if s.get("score", 0) <= 15)

    db_result = models.ScanResult(
        user_id=current_user.id,
        text_content=request.text_content[:30] + "... [PURGED FOR PRIVACY]",
        ai_probability=result["ai_probability"],
        perplexity=result["perplexity"],
        burstiness=result["burstiness"],
        status=result["status"],
        sentences=sentences, # Kept briefly for report download
        ai_count=ai_c,
        para_count=para_c,
        mix_count=mix_c,
        human_count=human_c
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    # 5. Background Maintenance (Safety Net with Delay)
    background_tasks.add_task(purge_sensitive_data, db)
    background_tasks.add_task(expire_old_history, db, 7) # Auto-expiry
    
    # Convert to schema and manually inject sentences for the initial view
    response_data = schemas.ScanResponse.model_validate(db_result)
    response_data.sentences = sentences
    return response_data

@app.get("/history", response_model=list[schemas.ScanResponse])
async def get_history(
    limit: int = 10, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Filter by user unless admin
    query = db.query(models.ScanResult)
    if current_user.role != "admin":
        query = query.filter(models.ScanResult.user_id == current_user.id)
        
    return query.order_by(models.ScanResult.created_at.desc()).limit(limit).all()

@app.delete("/history")
async def clear_history(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    count = delete_user_history(db, current_user.id)
    return {"message": f"Berhasil menghapus {count} riwayat scan.", "deleted_count": count}

@app.post("/analyze-file", response_model=schemas.ScanResponse)
async def analyze_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Read file content & Extraction
    content = await file.read()
    try:
        text = doc_processor.process_file(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="Gagal mengekstrak teks dari file.")

    # 2. Tier Checks (Word Count & Quota for Free)
    words = text.split()
    word_count = len(words)
    
    if current_user.role == "free":
        if word_count > 800:
            raise HTTPException(
                status_code=403, 
                detail=f"Batas gratis 800 kata terlampaui (File ini: {word_count} kata). Silakan upgrade ke Pro!"
            )
        if current_user.daily_quota <= 0:
            raise HTTPException(
                status_code=403, 
                detail="Kuota harian gratis Anda sudah habis. Silakan balik lagi besok atau upgrade ke Pro!"
            )

    # 3. Analyze (Pro/Admin bypass Hybrid Sampling)
    force_full = current_user.role in ["pro", "admin"]
    result = detector.analyze(text, force_full_scan=force_full)
    
    # 4. Deduct Quota for Free Users
    if current_user.role == "free":
        current_user.daily_quota -= 1
    
    # 5. Save to DB (Metadata persistent, sentences kept briefly)
    sentences = result.get("sentences", [])
    ai_c = sum(1 for s in sentences if s.get("score", 0) > 70)
    para_c = sum(1 for s in sentences if 40 < s.get("score", 0) <= 70)
    mix_c = sum(1 for s in sentences if 15 < s.get("score", 0) <= 40)
    human_c = sum(1 for s in sentences if s.get("score", 0) <= 15)

    db_result = models.ScanResult(
        user_id=current_user.id,
        text_content=file.filename[:30] + "... [PURGED FOR PRIVACY]",
        ai_probability=result["ai_probability"],
        perplexity=result["perplexity"],
        burstiness=result["burstiness"],
        status=result["status"],
        sentences=sentences, # Kept briefly for report download
        ai_count=ai_c,
        para_count=para_c,
        mix_count=mix_c,
        human_count=human_c
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    # 6. Background Maintenance (Safety Net with Delay)
    background_tasks.add_task(purge_sensitive_data, db)
    background_tasks.add_task(expire_old_history, db, 7) # Auto-expiry
    
    # Convert to schema and inject sentences for initial view
    response_data = schemas.ScanResponse.model_validate(db_result)
    response_data.sentences = sentences
    return response_data

@app.get("/report/{scan_id}")
async def generate_report(
    scan_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    scan = db.query(models.ScanResult).filter(models.ScanResult.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Hasil scan tidak ditemukan.")
    
    # Security: Only owner or admin can download report
    if scan.user_id != current_user.id and current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke laporan ini.")
    
    # Prepare data for report generator
    scan_data = {
        "ai_probability": scan.ai_probability,
        "status": scan.status,
        "perplexity": scan.perplexity,
        "burstiness": scan.burstiness,
        "created_at": scan.created_at.strftime("%Y-%m-%d %H:%M"),
        "sentences": scan.sentences,
        "ai_count": scan.ai_count,
        "para_count": scan.para_count,
        "mix_count": scan.mix_count,
        "human_count": scan.human_count
    }
    
    # Generate PDF
    pdf_bytes = report_gen.generate_scan_report(scan_data)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=SahihAksara_Report_{scan_id}.pdf"}
    )

# --- PAYMENT ENDPOINTS (UNIKAPAY) ---

@app.post("/payments/create")
async def create_payment(
    plan_type: str = "monthly", # default to monthly
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Fetch price and discount from settings
    if plan_type == "daily":
        price_key = "pro_day_price"
        discount_key = "pro_day_discount_percent"
    else:
        price_key = "pro_monthly_price"
        discount_key = "pro_discount_percent"

    base_price_setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == price_key).first()
    discount_percent_setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == discount_key).first()
    discount_active_setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == "is_discount_active").first()
    
    base_price = float(base_price_setting.value) if base_price_setting else 50000
    discount_percent = float(discount_percent_setting.value) if discount_percent_setting else 0
    is_discount_active = (discount_active_setting.value.lower() == "true") if discount_active_setting else False
    
    amount = base_price
    if is_discount_active:
        amount = base_price * (1 - discount_percent / 100)
        
    order_id = f"SA-{uuid.uuid4().hex[:8].upper()}"
    
    # 1. Create local transaction record
    new_tx = models.Transaction(
        user_id=current_user.id,
        order_id=order_id,
        amount=amount,
        plan_type=plan_type,
        status="pending"
    )
    db.add(new_tx)
    db.commit()
    
    # 2. Call UnikaPay API
    payload = {
        "order_id": order_id,
        "amount": amount,
        "customer_details": {
            "first_name": current_user.full_name or "User",
            "email": current_user.email,
        },
        "item_details": [
            {
                "id": f"PRO-{plan_type.upper()}",
                "price": amount,
                "quantity": 1,
                "name": f"SahihAksara Pro {plan_type.title()}"
            }
        ]
    }
    
    headers = {
        "X-API-KEY": UNIKAPAY_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{UNIKAPAY_BASE_URL}/gateway/api/pay",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        return data # {token, redirect_url}
    except Exception as e:
        db.delete(new_tx)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Gagal menghubungi gateway pembayaran: {str(e)}")

@app.post("/payments/webhook")
async def payment_webhook(request: Request, db: Session = Depends(database.get_db)):
    # 1. Get raw body for signature verification
    raw_body = await request.body()
    signature = request.headers.get("X-Unikapay-Signature")
    
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    # 2. Verify Signature (HMAC-SHA512)
    expected_signature = hmac.new(
        UNIKAPAY_API_KEY.encode(),
        raw_body,
        hashlib.sha512
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
        
    # 3. Process Payload
    data = await request.json()
    order_id = data.get("order_id")
    status = data.get("transaction_status")
    
    tx = db.query(models.Transaction).filter(models.Transaction.order_id == order_id).first()
    if not tx:
        return {"message": "Transaction not found"}
        
    # 4. Handle Success (Settlement)
    if status == "settlement" and tx.status != "settlement":
        tx.status = "settlement"
        # Upgrade User
        user = db.query(models.User).filter(models.User.id == tx.user_id).first()
        if user:
            user.role = "pro"
            user.daily_quota = 99999 # Infinite for Pro
            
            # Calculate Expiry
            from datetime import timedelta
            now = datetime.datetime.utcnow()
            
            if tx.plan_type == "daily":
                expiry = now + timedelta(days=1)
            else: # monthly
                expiry = now + timedelta(days=30)
                
            user.pro_expires_at = expiry
            
        db.commit()
    elif status in ["expire", "deny", "cancel"]:
        tx.status = status
        db.commit()
        
    return {"message": "Webhook processed"}

@app.get("/payments/webhook")
async def payment_webhook_verify():
    return {"message": "SahihAksara Payment Webhook is Active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# --- ADMIN ENDPOINTS ---

@app.get("/admin/users", response_model=List[schemas.UserResponse])
def admin_get_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    admin: models.User = Depends(get_current_admin_user)
):
    return db.query(models.User).offset(skip).limit(limit).all()

@app.patch("/admin/users/{user_id}", response_model=schemas.UserResponse)
def admin_update_user(
    user_id: int, 
    update: schemas.UserAdminUpdate, 
    db: Session = Depends(database.get_db),
    admin: models.User = Depends(get_current_admin_user)
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")
    
    if update.role is not None:
        db_user.role = update.role
    if update.daily_quota is not None:
        db_user.daily_quota = update.daily_quota
        
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/admin/stats", response_model=schemas.AdminStats)
def admin_get_stats(
    db: Session = Depends(database.get_db),
    admin: models.User = Depends(get_current_admin_user)
):
    total_users = db.query(models.User).count()
    total_scans = db.query(models.ScanResult).count()
    pro_users = db.query(models.User).filter(models.User.role == "pro").count()
    
    # Simple scans today (dummy logic for now, can be improved with created_at filtering)
    from datetime import datetime, date
    today = date.today()
    scans_today = db.query(models.ScanResult).filter(func.date(models.ScanResult.created_at) == today).count()
    
    return {
        "total_users": total_users,
        "total_scans": total_scans,
        "pro_users": pro_users,
        "scans_today": scans_today
    }

@app.get("/admin/settings")
def admin_get_settings(
    db: Session = Depends(database.get_db),
    admin: models.User = Depends(get_current_admin_user)
):
    # Ensure default settings exist
    defaults = {
        "pro_monthly_price": ("100000", "Base price for Pro Monthly subscription"),
        "pro_discount_percent": ("0", "Discount percentage for Monthly (0-100)"),
        "pro_day_price": ("15000", "Base price for Pro Day Pass"),
        "pro_day_discount_percent": ("0", "Discount percentage for Day Pass (0-100)"),
        "is_discount_active": ("false", "Toggle to enable/disable discount")
    }
    
    for key, (val, desc) in defaults.items():
        setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == key).first()
        if not setting:
            new_setting = models.SystemSetting(key=key, value=val, description=desc)
            db.add(new_setting)
    db.commit()
    
    return db.query(models.SystemSetting).all()

@app.get("/settings")
def get_public_settings(
    db: Session = Depends(database.get_db)
):
    # Public endpoint for pricing settings - similar to admin but no auth required
    defaults = {
        "pro_monthly_price": ("100000", "Base price for Pro Monthly subscription"),
        "pro_discount_percent": ("0", "Discount percentage for Monthly (0-100)"),
        "pro_day_price": ("15000", "Base price for Pro Day Pass"),
        "pro_day_discount_percent": ("0", "Discount percentage for Day Pass (0-100)"),
        "is_discount_active": ("false", "Toggle to enable/disable discount")
    }
    
    # Ensure defaults exist
    for key, (val, desc) in defaults.items():
        setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == key).first()
        if not setting:
            new_setting = models.SystemSetting(key=key, value=val, description=desc)
            db.add(new_setting)
    db.commit()

    return db.query(models.SystemSetting).all()

@app.patch("/admin/settings/{key}")
def admin_update_setting(
    key: str,
    update: dict,
    db: Session = Depends(database.get_db),
    admin: models.User = Depends(get_current_admin_user)
):
    setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting tidak ditemukan.")
    
    if "value" in update:
        setting.value = str(update["value"])
        db.commit()
        db.refresh(setting)
    
    return setting

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
