import models
import database
import bcrypt
from sqlalchemy.orm import Session

db = next(database.get_db())

admin_email = "admin@sahihaksara.id"
admin_pwd = "admin123"

# Hash manually to avoid passlib+bcrypt issues
salt = bcrypt.gensalt()
hashed_pwd = bcrypt.hashpw(admin_pwd.encode('utf-8'), salt).decode('utf-8')

# Check if exists
existing = db.query(models.User).filter(models.User.email == admin_email).first()
if not existing:
    new_admin = models.User(
        email=admin_email,
        hashed_password=hashed_pwd,
        full_name="Super Admin",
        role="admin",
        daily_quota=99999
    )
    db.add(new_admin)
    db.commit()
    print(f"✅ Admin created! Email: {admin_email} | Password: {admin_pwd}")
else:
    existing.role = "admin"
    existing.hashed_password = hashed_pwd # Update password too
    db.commit()
    print(f"ℹ️ User {admin_email} updated. Role set to admin and password reset.")
