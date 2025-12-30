import sys
import os
sys.path.append(os.getcwd() + "/backend")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
from models import ScanResult
from database import SQLALCHEMY_DATABASE_URL
from core.maintenance import purge_sensitive_data, delete_user_history

# Test Zero-Retention implementation
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def verify_retention():
    print("--- SAHIHAKSARA ZERO-RETENTION AUDIT ---")
    
    # 1. Immediate Purge Check (Already processed scans)
    print("\n[STEP 1] Checking Immediate On-Write Purge...")
    scans = db.query(ScanResult).order_by(ScanResult.created_at.desc()).limit(5).all()
    
    if not scans:
        print("No scans found to verify.")
    else:
        for scan in scans:
            print(f"Audit Scan ID: {scan.id}")
            if "PURGED" in scan.text_content:
                print(f"  [PASS] Text Purged: {scan.text_content}")
            else:
                print(f"  [FAIL] Text NOT Purged: {scan.text_content[:50]}")
            
            if scan.sentences is None:
                print("  [PASS] Sentences Purged.")
            else:
                print("  [FAIL] Sentences STILL in database.")

    # 2. Background Purge Check (Manual Trigger)
    print("\n[STEP 2] Testing Background Maintenance Purge...")
    # Simulate a "leaked" record (old scan not purged correctly)
    # Note: In production, we don't 'leak' but we test the safety net.
    purged_count = purge_sensitive_data(db, older_than_hours=0) # Force purge all
    print(f"  Handled {purged_count} records via maintenance purge.")

    # 3. Manual History Clear Check
    print("\n[STEP 3] Testing User History Clear...")
    user = db.query(models.User).filter(models.User.role != "admin").first()
    if user:
        deleted = delete_user_history(db, user.id)
        print(f"  Deleted {deleted} history records for user {user.email}")
        
        remaining = db.query(ScanResult).filter(ScanResult.user_id == user.id).count()
        if remaining == 0:
            print("  [PASS] History fully cleared.")
        else:
            print(f"  [FAIL] {remaining} records still remain.")
    else:
        print("  Skipping Step 3: No test user found.")

    print("\n--- AUDIT COMPLETE ---")

if __name__ == "__main__":
    verify_retention()
