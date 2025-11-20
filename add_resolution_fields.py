import sqlite3
import os

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'reports.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add resolution_notes column
        cursor.execute("ALTER TABLE report ADD COLUMN resolution_notes VARCHAR(500)")
        print("Added resolution_notes column")
    except sqlite3.OperationalError:
        print("resolution_notes column already exists")
    
    try:
        # Add resolution_image column
        cursor.execute("ALTER TABLE report ADD COLUMN resolution_image VARCHAR(100)")
        print("Added resolution_image column")
    except sqlite3.OperationalError:
        print("resolution_image column already exists")
    
    conn.commit()
    conn.close()
    print("\nDatabase updated successfully!")
    print("New features ready to use:")
    print("  - Camera capture for reports")
    print("  - Resolution notes and images")
else:
    print("Database not found. Run: python migrate_database.py first")
