#!/usr/bin/env python3
"""
Migration script to import clubs from CSV files into the database.
Imports clubs from clubs.csv into the clubs table.
"""

import csv
import os
import sys
from db import get_connection

def import_clubs_from_csv(csv_path='clubs.csv'):
    """
    Import clubs from CSV file into the clubs table.
    
    Args:
        csv_path: Path to the CSV file (relative to backend directory)
    """
    # Get absolute path to CSV file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(base_dir, csv_path)
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        return False
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            imported = 0
            skipped = 0
            errors = []
            
            for row in reader:
                club_id = row.get('id', '').strip()
                name = row.get('name', '').strip()
                description = row.get('description', '').strip()
                category = row.get('category', '').strip()
                contact = row.get('contact', '').strip()
                image_url = row.get('image_url', '').strip()
                
                if not name:
                    print(f"Warning: Skipping row with empty name (ID: {club_id})")
                    skipped += 1
                    continue
                
                # Check if club already exists (by name)
                check_sql = "SELECT id FROM clubs WHERE name = %s"
                cur.execute(check_sql, (name,))
                existing = cur.fetchone()
                
                if existing:
                    print(f"Skipping '{name}' - already exists (ID: {existing[0]})")
                    skipped += 1
                    continue
                
                # Insert club into clubs table
                insert_sql = """
                    INSERT INTO clubs (name, description, category, contact, image_url)
                    VALUES (%s, %s, %s, %s, %s)
                """
                
                try:
                    cur.execute(insert_sql, (
                        name,
                        description or None,
                        category or None,
                        contact or None,
                        image_url or None
                    ))
                    imported += 1
                    print(f"[OK] Imported: {name}")
                except Exception as e:
                    error_msg = f"Error importing '{name}': {str(e)}"
                    print(f"[ERROR] {error_msg}")
                    errors.append(error_msg)
            
            conn.commit()
            
            print(f"\n{'='*60}")
            print(f"Import Summary:")
            print(f"  Imported: {imported}")
            print(f"  Skipped: {skipped}")
            if errors:
                print(f"  Errors: {len(errors)}")
            print(f"{'='*60}")
            
            if errors:
                print("\nErrors encountered:")
                for error in errors:
                    print(f"  - {error}")
            
            return True
            
    except Exception as e:
        conn.rollback()
        print(f"Error during import: {str(e)}")
        return False
    finally:
        cur.close()
        conn.close()

def import_groups_as_clubs(csv_path='groups.csv'):
    """
    Import groups from groups.csv as clubs (optional).
    Useful if you want to make groups available as clubs.
    """
    print("\n" + "="*60)
    print("Importing groups as clubs...")
    print("="*60 + "\n")
    return import_clubs_from_csv(csv_path)

def main():
    """Main function to run the import."""
    print("="*60)
    print("Club Import Script")
    print("="*60)
    print("\nThis script will import clubs from clubs.csv into the database.")
    print("Existing clubs (by name) will be skipped.\n")
    
    # Import clubs from clubs.csv
    print("Importing clubs from clubs.csv...")
    print("-"*60)
    success = import_clubs_from_csv('clubs.csv')
    
    if not success:
        print("\nFailed to import clubs. Please check the error messages above.")
        sys.exit(1)
    
    # Ask if user wants to import groups as clubs too
    print("\n" + "="*60)
    try:
        response = input("\nDo you also want to import groups from groups.csv as clubs? (y/n): ").strip().lower()
        
        if response == 'y':
            import_groups_as_clubs('groups.csv')
    except EOFError:
        # Non-interactive mode - skip groups import
        print("\n(Skipping groups import - non-interactive mode)")
    
    print("\n[OK] Import complete!")

if __name__ == '__main__':
    main()

