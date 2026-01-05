from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, BackgroundTasks, Form, status
from fastapi.responses import JSONResponse, Response, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from langdetect import detect, DetectorFactory
import hashlib
DetectorFactory.seed = 0 # For consistent results
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
from core.config import settings

# Initialize database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title=settings.PROJECT_NAME, description="API for Indonesian AI Content Detection")

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
# Use absolute path for logo to avoid issues with different CWDs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "assets", "logo.png")
report_gen = ReportGenerator(logo_path=logo_path)

# Setup CORS for Nuxt.js frontend
# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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
    # 0. Language Guard: Check if text is Indonesian
    try:
        lang = detect(request.text_content)
        if lang == 'en':
            raise HTTPException(
                status_code=400,
                detail="SahihAksara dioptimasi khusus untuk mendeteksi struktur dan pola Bahasa Indonesia guna menjamin akurasi 99%. Kami mendeteksi naskah Anda menggunakan Bahasa Inggris. Untuk hasil terbaik, silakan gunakan teks berbahasa Indonesia atau detektor internasional."
            )
    except HTTPException:
        raise
    except Exception:
        # Ignore detection errors for very short or non-textual content, fallback to analyzer
        pass

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
    
    # Calculate Fingerprint (SHA-256)
    text_hash = hashlib.sha256(request.text_content.encode()).hexdigest()

    db_result = models.ScanResult(
        user_id=current_user.id,
        text_content=request.text_content[:30] + "... [PURGED FOR PRIVACY]",
        sha256_hash=text_hash,
        ai_probability=result["ai_probability"],
        perplexity=result["perplexity"],
        burstiness=result["burstiness"],
        status=result["status"],
        sentences=sentences, # Kept briefly for report download
        ai_count=result.get("ai_count", 0),
        para_count=result.get("para_count", 0),
        mix_count=result.get("mix_count", 0),
        human_count=result.get("human_count", 0),
        citation_count=result.get("citation_count", 0),
        skipped_count=result.get("skipped_count", 0),
        opinion_semantic=result.get("opinion_semantic"),
        opinion_perplexity=result.get("opinion_perplexity"),
        opinion_burstiness=result.get("opinion_burstiness"),
        opinion_humanity=result.get("opinion_humanity"),
        citation_percentage=result.get("citation_percentage"),
        ai_source=result.get("ai_source")
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    # 5. Background Maintenance (Safety Net with Delay)
    background_tasks.add_task(purge_sensitive_data, db)
    background_tasks.add_task(expire_old_history, db, 7) # Auto-expiry
    
    # Convert to schema and manually inject sentences for the initial view
    # We explicitly return the full text here so the frontend can use it immediately (e.g. for Humanizer)
    # Even though it's saved as 'PURGED' in the database for long-term privacy.
    response_data = schemas.ScanResponse.model_validate(db_result)
    response_data.text_content = request.text_content 
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
        raise HTTPException(status_code=400, detail="Gagal mengekstrak teks dari berkas.")

    # 0. Language Guard
    try:
        lang = detect(text) 
        if lang == 'en':
            raise HTTPException(
                status_code=400,
                detail="SahihAksara dioptimasi khusus untuk mendeteksi struktur dan pola Bahasa Indonesia guna menjamin akurasi 99%. Kami mendeteksi naskah Anda menggunakan Bahasa Inggris. Untuk hasil terbaik, silakan gunakan teks berbahasa Indonesia atau detektor internasional."
            )
    except HTTPException:
        raise
    except Exception:
        pass

    # 1. Freemium Logic
    # Tier Checks (Word Count & Quota for Free)
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
    
    # Calculate Fingerprint
    text_hash = hashlib.sha256(text.encode()).hexdigest()

    db_result = models.ScanResult(
        user_id=current_user.id,
        text_content=file.filename[:30] + "... [PURGED FOR PRIVACY]",
        sha256_hash=text_hash,
        ai_probability=result["ai_probability"],
        perplexity=result["perplexity"],
        burstiness=result["burstiness"],
        status=result["status"],
        sentences=sentences, # Kept briefly for report download
        ai_count=result.get("ai_count", 0),
        para_count=result.get("para_count", 0),
        mix_count=result.get("mix_count", 0),
        human_count=result.get("human_count", 0),
        citation_count=result.get("citation_count", 0),
        skipped_count=result.get("skipped_count", 0),
        opinion_semantic=result.get("opinion_semantic"),
        opinion_perplexity=result.get("opinion_perplexity"),
        opinion_burstiness=result.get("opinion_burstiness"),
        opinion_humanity=result.get("opinion_humanity"),
        citation_percentage=result.get("citation_percentage"),
        ai_source=result.get("ai_source")
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    # 6. Background Maintenance (Safety Net with Delay)
    background_tasks.add_task(purge_sensitive_data, db)
    background_tasks.add_task(expire_old_history, db, 7) # Auto-expiry
    
    # Convert to schema and inject sentences for initial view
    response_data = schemas.ScanResponse.model_validate(db_result)
    response_data.text_content = text
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
        "id": scan.id,
        "ai_probability": scan.ai_probability,
        "status": scan.status,
        "perplexity": scan.perplexity,
        "burstiness": scan.burstiness,
        "created_at": scan.created_at.strftime("%Y-%m-%d %H:%M"),
        "sentences": scan.sentences,
        "ai_count": scan.ai_count,
        "para_count": scan.para_count,
        "mix_count": scan.mix_count,
        "human_count": scan.human_count,
        "citation_count": scan.citation_count,
        "skipped_count": scan.skipped_count,
        "opinion_semantic": scan.opinion_semantic,
        "opinion_perplexity": scan.opinion_perplexity,
        "opinion_burstiness": scan.opinion_burstiness,
        "citation_percentage": scan.citation_percentage
    }
    
    # Generate PDF
    pdf_bytes = report_gen.generate_scan_report(scan_data)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=SahihAksara_Report_{scan_id}.pdf"}
    )


@app.get("/download-certificate/{scan_id}")
async def download_certificate(scan_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    scan = db.query(models.ScanResult).filter(models.ScanResult.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Hasil scan tidak ditemukan.")
    
    # Security: Only owner or admin
    if scan.user_id != current_user.id and current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke sertifikat ini.")
    
    # Threshold Check: Must be <= 45% AI (Adjusted for Academic/Scientific Rigidity)
    if scan.ai_probability > 45:
        raise HTTPException(
            status_code=400, 
            detail=f"Sertifikat Keaslian hanya diterbitkan untuk skor AI di bawah 45% (Skor Anda: {scan.ai_probability}%)."
        )
    
    # Prepare data
    cert_data = {
        "id": scan.id,
        "ai_probability": scan.ai_probability,
        "status": scan.status,
        "created_at": scan.created_at.strftime("%B %d, %Y"),
        "sha256_hash": scan.sha256_hash or "N/A",
        "full_name": current_user.full_name or "Verified User"
    }
    
    # Generate Cert (Landscape)
    cert_bytes = report_gen.generate_authenticity_certificate(cert_data)
    
    return Response(
        content=cert_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=SahihAksara_Certificate_{scan_id}.pdf"}
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
            f"{settings.UNIKAPAY_BASE_URL}/gateway/api/pay",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        
        # Save Snap Token
        if "token" in data:
            new_tx.snap_token = data["token"]
            db.commit()
            
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
        settings.UNIKAPAY_API_KEY.encode(),
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

@app.get("/payments/history", response_model=List[schemas.TransactionResponse])
async def get_payment_history(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    history = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).order_by(models.Transaction.created_at.desc()).all()
    return history


@app.get("/health/gateway")
async def check_gateway_health():
    """
    Checks if the payment gateway (UnikaPay) is online.
    """
    try:
        response = requests.get(f"{settings.UNIKAPAY_BASE_URL}/gateway/health", timeout=3)
        if response.status_code == 200:
            return {"online": True}
        return {"online": False, "status_code": response.status_code}
    except Exception as e:
        return {"online": False, "error": str(e)}

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
    if update.is_active is not None:
        db_user.is_active = update.is_active
        
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

@app.get("/verify/{scan_id}", response_class=HTMLResponse)
async def verify_report(scan_id: int, db: Session = Depends(database.get_db)):
    # Public verification of report authenticity
    scan = db.query(models.ScanResult).filter(models.ScanResult.id == scan_id).first()
    
    if not scan:
        return """
        <html>
            <head>
                <title>Laporan Tidak Valid | SahihAksara</title>
                <style>
                    body { font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; background: #fef2f2; }
                    .card { background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); text-align: center; }
                    h1 { color: #ef4444; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>❌ Laporan Tidak Terverifikasi</h1>
                    <p>ID Laporan tidak ditemukan dalam sistem kami.</p>
                </div>
            </body>
        </html>
        """

    # Format Date
    formatted_date = scan.created_at.strftime("%B %d, %Y")
    status_color = "#ef4444" if scan.ai_probability > 75 else "#f59e0b" if scan.ai_probability > 40 else "#10b981"
    
    # Certificate Status
    cert_html = ""
    if scan.ai_probability <= 45:
        cert_html = """
        <div style="background: #fef3c7; color: #92400e; padding: 12px; border-radius: 12px; font-size: 13px; font-weight: 600; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; gap: 8px; border: 1px solid #fde68a;">
            <span>🏅</span> GOLD STATUS: Originality Certified
        </div>
        """

    # Minimalist verified UI
    return f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verifikasi Laporan SahihAksara</title>
        <style>
            :root {{
                --primary: #7c3aed;
                --emerald: #10b981;
                --slate: #1e293b;
            }}
            body {{ font-family: 'Inter', -apple-system, sans-serif; background: #f8fafc; color: var(--slate); display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }}
            .card {{ background: white; max-width: 450px; width: 100%; padding: 40px; border-radius: 24px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.05); text-align: center; position: relative; overflow: hidden; }}
            .card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 6px; background: var(--primary); }}
            .icon-check {{ width: 64px; height: 64px; background: #dcfce7; color: var(--emerald); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; margin: 0 auto 24px; }}
            h1 {{ font-size: 24px; margin: 0 0 8px; color: var(--slate); }}
            .verified-tag {{ color: var(--emerald); font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 24px; display: block; }}
            .info-box {{ background: #f1f5f9; padding: 24px; border-radius: 16px; margin: 24px 0; }}
            .label {{ font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; display: block; }}
            .value {{ font-size: 20px; font-weight: 700; color: var(--slate); }}
            .score-badge {{ display: inline-block; padding: 4px 12px; border-radius: 999px; font-weight: 700; color: white; background: {status_color}; margin-top: 8px; }}
            .fingerprint {{ font-family: monospace; font-size: 10px; color: #94a3b8; word-break: break-all; margin-top: 20px; border-top: 1px dashed #e2e8f0; padding-top: 10px; }}
            .footer {{ font-size: 12px; color: #94a3b8; margin-top: 32px; }}
            .logo {{ font-weight: 800; color: var(--primary); font-size: 18px; margin-bottom: 32px; display: block; }}
        </style>
    </head>
    <body>
        <div class="card">
            <span class="logo">SahihAksara</span>
            
            {cert_html}

            <div class="icon-check">✓</div>
            <h1>Laporan Asli (Verified)</h1>
            <span class="verified-tag">Dokumen Terverifikasi Digital</span>
            
            <div class="info-box">
                <span class="label">ID Laporan #000{scan.id}</span>
                <span class="value">{formatted_date}</span>
                <br><br>
                <span class="label">Hasil Analisis</span>
                <span class="value">{scan.status}</span>
                <br>
                <div class="score-badge">{scan.ai_probability}% AI Probability</div>
            </div>

            <p style="font-size: 13px; color: #64748b; line-height: 1.6;">Laporan ini dinyatakan asli dan dikeluarkan oleh sistem SahihAksara AI Detector. Seluruh data pada dokumen fisik sesuai dengan record digital kami.</p>
            
            <div class="fingerprint">
                SHA-256 Fingerprint:<br>
                {scan.sha256_hash or 'N/A'}
            </div>

            <div class="footer">
                &copy; 2025 SahihAksara Integrity System<br>
                Universitas Kutai Kartanegara
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
