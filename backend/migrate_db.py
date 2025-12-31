import database
from sqlalchemy import text

db = next(database.get_db())

try:
    print("🚀 Starting manual migration...")
    
    # 1. Check users table
    print("Checking 'users' table columns...")
    # Add columns if they don't exist
    cols_to_add = [
        ("hashed_password", "VARCHAR"),
        ("full_name", "VARCHAR"),
        ("role", "VARCHAR DEFAULT 'free'"),
        ("daily_quota", "INTEGER DEFAULT 5"),
        ("pro_expires_at", "TIMESTAMP")
    ]
    
    for col_name, col_type in cols_to_add:
        try:
            db.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};"))
            db.commit()
            print(f"✅ Added {col_name} to users")
        except Exception as e:
            db.rollback()
            if "already exists" in str(e):
                print(f"ℹ️ {col_name} already exists in users")
            else:
                print(f"❌ Error adding {col_name} to users: {e}")

    # 2. Check scan_results table
    print("\nChecking 'scan_results' table columns...")
    scan_cols = [
        ("user_id", "INTEGER REFERENCES users(id)"),
        ("ai_count", "INTEGER DEFAULT 0"),
        ("para_count", "INTEGER DEFAULT 0"),
        ("mix_count", "INTEGER DEFAULT 0"),
        ("human_count", "INTEGER DEFAULT 0"),
        ("opinion_semantic", "FLOAT"),
        ("opinion_perplexity", "FLOAT"),
        ("opinion_burstiness", "FLOAT"),
        ("opinion_humanity", "FLOAT"),
    ]
    for col_name, col_type in scan_cols:
        try:
            db.execute(text(f"ALTER TABLE scan_results ADD COLUMN {col_name} {col_type};"))
            db.commit()
            print(f"✅ Added {col_name} to scan_results")
        except Exception as e:
            db.rollback()
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print(f"ℹ️ {col_name} already exists in scan_results")
            else:
                print(f"❌ Error adding {col_name} to scan_results: {e}")

    # 3. Check transactions table
    print("\nChecking 'transactions' table columns...")
    try:
        db.execute(text("ALTER TABLE transactions ADD COLUMN plan_type VARCHAR;"))
        db.commit()
        print("✅ Added plan_type to transactions")
    except Exception as e:
        db.rollback()
        if "already exists" in str(e) or "duplicate column" in str(e).lower():
            print("ℹ️ plan_type already exists in transactions")
        else:
            print(f"❌ Error adding plan_type to transactions: {e}")

    try:
        db.execute(text("ALTER TABLE transactions ADD COLUMN snap_token VARCHAR;"))
        db.commit()
        print("✅ Added snap_token to transactions")
    except Exception as e:
        db.rollback()
        if "already exists" in str(e) or "duplicate column" in str(e).lower():
            print("ℹ️ snap_token already exists in transactions")
        else:
            print(f"❌ Error adding snap_token to transactions: {e}")

    # 3. Tables like 'transactions' will be created by create_all in main.py 
    # but let's be sure
    print("\nMigration finished. Running create_all just in case...")
    import models
    models.Base.metadata.create_all(bind=database.engine)
    print("✨ Database is now in sync!")

except Exception as e:
    print(f"💥 Migration failed: {e}")
