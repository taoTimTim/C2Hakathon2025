#!/usr/bin/env python3
"""
Script to add missing columns (category, contact, image_url) to the clubs table.
"""

from db import get_connection

def add_missing_columns():
    """Add missing columns to clubs table if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check and add category column
        try:
            cur.execute("ALTER TABLE clubs ADD COLUMN category VARCHAR(255)")
            print("[OK] Added 'category' column")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("[SKIP] 'category' column already exists")
            else:
                raise
        
        # Check and add contact column
        try:
            cur.execute("ALTER TABLE clubs ADD COLUMN contact VARCHAR(255)")
            print("[OK] Added 'contact' column")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("[SKIP] 'contact' column already exists")
            else:
                raise
        
        # Check and add image_url column
        try:
            cur.execute("ALTER TABLE clubs ADD COLUMN image_url VARCHAR(255)")
            print("[OK] Added 'image_url' column")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("[SKIP] 'image_url' column already exists")
            else:
                raise
        
        conn.commit()
        print("\n[OK] All columns added successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    print("="*60)
    print("Add Missing Columns to Clubs Table")
    print("="*60)
    print()
    add_missing_columns()

