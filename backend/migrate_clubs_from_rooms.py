#!/usr/bin/env python3
"""
Script to migrate clubs from the rooms table to the clubs table.
This moves CSV-imported clubs (is_system_generated=TRUE, created_by=NULL) 
from rooms to the clubs table before they're deleted.
"""

import sys
from db import get_connection

def preview_clubs_to_migrate():
    """
    Preview all CSV-imported clubs that will be migrated from rooms to clubs table.
    Returns the list of clubs.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Get only CSV-imported clubs (system-generated with no creator)
        sql = """
            SELECT r.id, r.name, r.description, r.created_at
            FROM rooms r
            WHERE r.room_type = 'club'
              AND r.is_system_generated = TRUE
              AND r.created_by IS NULL
            ORDER BY r.name ASC
        """
        
        cur.execute(sql)
        clubs = cur.fetchall()
        
        return clubs
        
    finally:
        cur.close()
        conn.close()

def migrate_clubs_from_rooms():
    """
    Migrate CSV-imported clubs from rooms table to clubs table.
    Only migrates clubs that don't already exist in clubs table (by name).
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Get clubs to migrate
        select_sql = """
            SELECT r.id, r.name, r.description, r.created_at
            FROM rooms r
            WHERE r.room_type = 'club'
              AND r.is_system_generated = TRUE
              AND r.created_by IS NULL
            ORDER BY r.name ASC
        """
        
        cur.execute(select_sql)
        clubs = cur.fetchall()
        
        if not clubs:
            print("No clubs found to migrate.")
            return 0, 0
        
        migrated = 0
        skipped = 0
        
        for club in clubs:
            name = club[1]  # name is at index 1
            description = club[2]  # description is at index 2
            created_at = club[3]  # created_at is at index 3
            
            # Check if club already exists in clubs table (by name)
            check_sql = "SELECT id FROM clubs WHERE name = %s"
            cur.execute(check_sql, (name,))
            existing = cur.fetchone()
            
            if existing:
                print(f"Skipping '{name}' - already exists in clubs table (ID: {existing[0]})")
                skipped += 1
                continue
            
            # Insert into clubs table
            # Note: category, contact, and image_url will be NULL since rooms table doesn't have them
            insert_sql = """
                INSERT INTO clubs (name, description, category, contact, image_url, created_at)
                VALUES (%s, %s, NULL, NULL, NULL, %s)
            """
            
            try:
                cur.execute(insert_sql, (name, description or None, created_at))
                migrated += 1
                print(f"✓ Migrated: {name}")
            except Exception as e:
                print(f"✗ Error migrating '{name}': {str(e)}")
                skipped += 1
        
        conn.commit()
        return migrated, skipped
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def main():
    """Main function to run the migration."""
    print("="*60)
    print("Migrate Clubs from Rooms to Clubs Table")
    print("="*60)
    print("\nThis script will migrate CSV-imported clubs from the rooms table")
    print("to the clubs table. Only clubs that don't already exist will be migrated.\n")
    
    # Preview what will be migrated
    print("Previewing clubs to migrate...")
    print("-"*60)
    clubs = preview_clubs_to_migrate()
    
    if not clubs:
        print("No CSV-imported clubs found in rooms table. Nothing to migrate.")
        return
    
    print(f"\nFound {len(clubs)} club(s) to migrate:\n")
    for club in clubs:
        print(f"  • {club['name']} (ID: {club['id']})")
    
    print("-"*60)
    print(f"Total clubs to migrate: {len(clubs)}")
    print("-"*60)
    
    # Ask for confirmation
    print("\nThis will copy clubs from rooms to clubs table.")
    response = input("\nDo you want to proceed with migration? (yes/no): ").strip().lower()
    
    if response not in ('yes', 'y'):
        print("\nMigration cancelled.")
        return
    
    # Perform migration
    print("\nMigrating clubs from rooms to clubs table...")
    try:
        migrated, skipped = migrate_clubs_from_rooms()
        print(f"\n✓ Migration complete!")
        print(f"  Migrated: {migrated}")
        print(f"  Skipped: {skipped} (already exist in clubs table)")
    except Exception as e:
        print(f"\n✗ Error during migration: {str(e)}")
        sys.exit(1)
    
    print("\n✓ You can now run remove_clubs_from_rooms.py to clean up the rooms table.")

if __name__ == '__main__':
    main()

