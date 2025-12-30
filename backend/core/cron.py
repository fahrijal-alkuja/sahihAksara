import sys
import os

# Add parent directory to path to import database and models
# Path: backend/core/cron.py -> parent is backend/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
import models
from sqlalchemy.orm import Session

def reset_daily_quotas():
    """
    Resets the daily quota to 5 for all users with the 'free' role.
    Run this script via a daily cron job at 00:00.
    """
    db: Session = database.SessionLocal()
    try:
        print("Starting daily quota reset...")
        affected_rows = db.query(models.User).filter(models.User.role == "free").update({"daily_quota": 5})
        db.commit()
        print(f"Daily quota reset complete. {affected_rows} free users updated.")
    except Exception as e:
        print(f"Error resetting quotas: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_daily_quotas()
