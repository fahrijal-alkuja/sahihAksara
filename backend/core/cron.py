import sys
import os

# Add parent directory to path to import database and models
# Path: backend/core/cron.py -> parent is backend/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
import models
import maintenance

def reset_daily_quotas():
    """
    Resets the daily quota to 5 for all users with the 'free' role.
    Also performs periodic database maintenance.
    Run this script via a daily cron job at 00:00.
    """
    db: Session = database.SessionLocal()
    try:
        print("--- STARTING DAILY MAINTENANCE ---")
        
        # 1. Reset Quotas
        print("Resetting daily quotas...")
        affected_rows = db.query(models.User).filter(models.User.role == "free").update({"daily_quota": 5})
        db.commit()
        print(f"Quotas reset complete. {affected_rows} free users updated.")
        
        # 2. Expire Old History (Older than 7 days metadata hard delete)
        print("Purging expired history (7+ days)...")
        expired_count = maintenance.expire_old_history(db, days=7)
        print(f"Purge complete. {expired_count} old records deleted.")
        
        # 3. Optimize DB
        print("Optimizing physical storage...")
        maintenance.vacuum_database(db)
        
        print("--- MAINTENANCE SUCCESSFUL ---")
    except Exception as e:
        print(f"Error during maintenance: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_daily_quotas()
