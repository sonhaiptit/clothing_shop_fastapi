"""
Database migration script to hash existing plain text passwords.

This script should be run ONCE to migrate existing plain text passwords
to hashed passwords using bcrypt.

WARNING: This will modify your database. Make a backup before running!
"""

import mysql.connector
from mysql.connector import Error
from auth import hash_password
from config import settings
from db import DB_CONFIG


def migrate_passwords():
    """Migrate plain text passwords to hashed passwords."""
    print("=" * 60)
    print("Password Migration Script")
    print("=" * 60)
    print("\nWARNING: This will modify all user passwords in the database.")
    print("Make sure you have a backup of your database before proceeding!")
    
    response = input("\nDo you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        return
    
    try:
        # Connect to database
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Get all users
        cursor.execute("SELECT maND, tenDangNhap, matKhau FROM nguoidung")
        users = cursor.fetchall()
        
        print(f"\nFound {len(users)} users to migrate.")
        
        migrated = 0
        skipped = 0
        
        for user in users:
            user_id = user['maND']
            username = user['tenDangNhap']
            password = user['matKhau']
            
            # Check if password is already hashed (bcrypt hashes start with $2b$)
            if password and password.startswith('$2b$'):
                print(f"Skipping {username} (already hashed)")
                skipped += 1
                continue
            
            # Hash the password
            hashed_password = hash_password(password)
            
            # Update the database
            cursor.execute(
                "UPDATE nguoidung SET matKhau = %s WHERE maND = %s",
                (hashed_password, user_id)
            )
            
            migrated += 1
            print(f"Migrated password for: {username}")
        
        # Commit changes
        connection.commit()
        
        print("\n" + "=" * 60)
        print(f"Migration complete!")
        print(f"Migrated: {migrated} users")
        print(f"Skipped: {skipped} users (already hashed)")
        print("=" * 60)
        
    except Error as e:
        print(f"\nError during migration: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    migrate_passwords()
