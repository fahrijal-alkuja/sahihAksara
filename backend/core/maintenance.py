from sqlalchemy.orm import Session
import models
import datetime
from typing import Optional

def purge_sensitive_data(db: Session, older_than_hours: int = 1):
    """
    Periodic maintenance: Ensure any potentially lingering sensitive data is wiped.
    This acts as a 'Safety Net' and enforces the Grace Period for Zero-Retention.
    Detailed sentence data (heatmap) is removed after 1 hour to allow user downloads.
    """
    try:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=older_than_hours)
        
        # 1. Purge sentences (Heatmap data) after the grace period
        scans_to_purge = db.query(models.ScanResult).filter(
            models.ScanResult.created_at < cutoff,
            models.ScanResult.sentences != None
        ).all()
        
        for scan in scans_to_purge:
            scan.sentences = None
            # Ensure text_content is also fully masked if it wasn't already
            if "[PURGED]" not in scan.text_content:
                scan.text_content = "[DATA EXPIRED & PURGED FOR PRIVACY]"
            
        db.commit()
        return len(scans_to_purge)
    except Exception as e:
        db.rollback()
        raise e

def expire_old_history(db: Session, days: int = 7):
    """
    Permanently delete all metadata for scans older than 'days' days.
    This is the final stage of Zero-Retention - even masked metadata is removed.
    """
    try:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        deleted_count = db.query(models.ScanResult).filter(
            models.ScanResult.created_at < cutoff
        ).delete()
        db.commit()
        return deleted_count
    except Exception as e:
        db.rollback()
        raise e

def delete_user_history(db: Session, user_id: int):
    """
    Hard delete of scan history for a specific user.
    """
    try:
        deleted_count = db.query(models.ScanResult).filter(models.ScanResult.user_id == user_id).delete()
        db.commit()
        return deleted_count
    except Exception as e:
        db.rollback()
        raise e

def vacuum_database(db: Session):
    """
    Physically optimizes the database disk space.
    VACUUM cannot be run inside a transaction block in PostgreSQL.
    We use the raw connection to execute it.
    """
    try:
        # Commit any pending transactions first
        db.commit()
        # Get raw connection
        connection = db.bind.raw_connection()
        connection.set_isolation_level(0) # AUTOCOMMIT
        cursor = connection.cursor()
        print("Starting physical database vacuum...")
        cursor.execute("VACUUM ANALYZE scan_results;")
        cursor.execute("REINDEX TABLE scan_results;")
        cursor.close()
        connection.close()
        print("Database optimization complete.")
        return True
    except Exception as e:
        print(f"Vacuum error: {e}")
        return False
