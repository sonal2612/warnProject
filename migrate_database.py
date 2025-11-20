import os
import shutil
from datetime import datetime

# Backup existing database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'reports.db')

if os.path.exists(db_path):
    backup_path = os.path.join(basedir, 'instance', f'reports_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    shutil.copy2(db_path, backup_path)
    print(f"Database backed up to: {backup_path}")
    os.remove(db_path)
    print("Old database removed")

# Create new database with updated schema
from app import app, db

with app.app_context():
    db.create_all()
    print("New database created with updated schema!")
    print("\nChanges made:")
    print("   - Added 'email' field to User model")
    print("   - Added 'reporter_email' field to Report model")
    print("   - Role selection now available during registration")
    print("\nNote: You need to re-register all users!")
    print("   Run: python create_admin.py to create admin user")
