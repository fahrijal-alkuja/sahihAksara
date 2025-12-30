import models
import database
from sqlalchemy.orm import Session

db = next(database.get_db())
users = db.query(models.User).all()

print("ID | EMAIL | NAME | ROLE")
print("-" * 30)
for u in users:
    print(f"{u.id} | {u.email} | {u.full_name} | {u.role}")
