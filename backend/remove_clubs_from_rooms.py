#!/usr/bin/env python3
"""
Script to remove clubs from the rooms table that were imported from CSV.
This safely removes only system-generated clubs (is_system_generated=TRUE, created_by=NULL)
and their related data.
"""

import sys
from db import get_connection

def preview_clubs_in_rooms():
    """
    Preview all CSV-imported clubs that will be deleted from the rooms table.
    Returns the list of clubs and related data counts.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Get only CSV-imported clubs (system-generated with no creator)
        sql = """
            SELECT r.id, r.name, r.description, r.created_at,
                   COUNT(DISTINCT rm.user_id) as members_count,
                   COUNT(DISTINCT m.id) as messages_count
            FROM rooms r
            LEFT JOIN room_members rm ON r.id = rm.room_id
            LEFT JOIN messages m ON r.id = m.room_id
            WHERE r.room_type = 'club'
              AND r.is_system_generated = TRUE
              AND r.created_by IS NULL
            GROUP BY r.id, r.name, r.description, r.created_at
            ORDER BY r.name ASC
        """
        
        cur.execute(sql)
        clubs = cur.fetchall()
        
        return clubs
        
    finally:
        cur.close()
        conn.close()

def remove_clubs_from_rooms():
    """
    Remove only CSV-imported clubs from the rooms table.
    Filters for: room_type='club' AND is_system_generated=TRUE AND created_by IS NULL
    This will also cascade delete related room_members and messages.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Get count before deletion for reporting
        cur.execute("""
            SELECT COUNT(*) FROM rooms 
            WHERE room_type = 'club' 
              AND is_system_generated = TRUE 
              AND created_by IS NULL
        """)
        count_before = cur.fetchone()[0]
        
        if count_before == 0:
            print("No CSV-imported clubs found in rooms table. Nothing to delete.")
            return 0
        
        # Delete only CSV-imported clubs from rooms table
        # CASCADE will automatically delete related room_members and messages
        delete_sql = """
            DELETE FROM rooms 
            WHERE room_type = 'club' 
              AND is_system_generated = TRUE 
              AND created_by IS NULL
        """
        cur.execute(delete_sql)
        
        conn.commit()
        deleted_count = cur.rowcount
        
        return deleted_count
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def main():
    """Main function to run the cleanup."""
    print("="*60)
    print("Remove CSV-Imported Clubs from Rooms Table")
    print("="*60)
    print("\nThis script will remove only clubs that were imported from CSV.")
    print("(Clubs with is_system_generated=TRUE and created_by=NULL)")
    print("Related data (room_members, messages) will also be deleted.\n")
    
    # Preview what will be deleted
    print("Previewing CSV-imported clubs that will be deleted...")
    print("-"*60)
    clubs = preview_clubs_in_rooms()
    
    if not clubs:
        print("No CSV-imported clubs found in rooms table. Nothing to delete.")
        return
    
    total_members = 0
    total_messages = 0
    
    print(f"\nFound {len(clubs)} CSV-imported club(s) in rooms table:\n")
    for club in clubs:
        members = club['members_count'] or 0
        messages = club['messages_count'] or 0
        total_members += members
        total_messages += messages
        
        print(f"  • {club['name']} (ID: {club['id']})")
        print(f"    - Members: {members}")
        print(f"    - Messages: {messages}")
        print()
    
    print("-"*60)
    print(f"Summary:")
    print(f"  CSV-imported clubs to delete: {len(clubs)}")
    print(f"  Total members: {total_members}")
    print(f"  Total messages: {total_messages}")
    print("-"*60)
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This action cannot be undone!")
    response = input("\nDo you want to proceed with deletion? (yes/no): ").strip().lower()
    
    if response not in ('yes', 'y'):
        print("\nDeletion cancelled.")
        return
    
    # Perform deletion
    print("\nDeleting CSV-imported clubs from rooms table...")
    try:
        deleted_count = remove_clubs_from_rooms()
        print(f"\n✓ Successfully deleted {deleted_count} CSV-imported club(s) from rooms table.")
        print("  (Related room_members and messages were also deleted via CASCADE)")
        print("  (User-created clubs in rooms table were NOT affected)")
    except Exception as e:
        print(f"\n✗ Error during deletion: {str(e)}")
        sys.exit(1)
    
    print("\n✓ Cleanup complete!")

if __name__ == '__main__':
    main()

