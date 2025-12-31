from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def migrate():
    columns_to_add = [
        ("sha256_hash", "VARCHAR"),
        ("opinion_semantic", "FLOAT"),
        ("opinion_perplexity", "FLOAT"),
        ("opinion_burstiness", "FLOAT"),
        ("opinion_humanity", "FLOAT"),
    ]
    
    with engine.connect() as conn:
        print("Checking for missing columns in 'scan_results'...")
        for col_name, col_type in columns_to_add:
            try:
                # PostgreSQL specific check for column existence
                query = text(f"""
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name='scan_results' AND column_name='{col_name}';
                """)
                result = conn.execute(query).fetchone()
                
                if not result:
                    print(f"Adding column '{col_name}'...")
                    conn.execute(text(f"ALTER TABLE scan_results ADD COLUMN {col_name} {col_type};"))
                    conn.commit()
                    print(f"Column '{col_name}' added successfully.")
                else:
                    print(f"Column '{col_name}' already exists.")
            except Exception as e:
                print(f"Error adding column '{col_name}': {e}")

if __name__ == "__main__":
    migrate()
