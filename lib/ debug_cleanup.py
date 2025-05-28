# lib/debug_cleanup.py
"""
Debug and cleanup script for Personal Finance Tracker.
Use this to investigate database issues and clean up test data.
"""

from models import create_tables, get_session
from models.user import User
from models.category import Category
from models.transaction import Transaction
import sqlite3

def inspect_database():
    """Inspect the database directly to see what's actually stored"""
    print("🔍 INSPECTING DATABASE...")
    print("="*50)
    
    try:
        # Connect directly to SQLite to see raw data
        conn = sqlite3.connect('finance_tracker.db')
        cursor = conn.cursor()
        
        # Check users table
        print("\n👥 USERS TABLE:")
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        print("Raw data:", users)
        
        if users:
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            print("Columns:", columns)
            
            for user in users:
                print(f"User record: {dict(zip(columns, user))}")
        else:
            print("No users found in database")
        
        # Check categories table
        print("\n📁 CATEGORIES TABLE:")
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        print("Categories count:", len(categories))
        
        # Check transactions table
        print("\n💰 TRANSACTIONS TABLE:")
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()
        print("Transactions count:", len(transactions))
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error inspecting database: {e}")

def test_user_operations():
    """Test user operations to identify issues"""
    print("\n🧪 TESTING USER OPERATIONS...")
    print("="*50)
    
    try:
        # Test User.get_all()
        print("\nTesting User.get_all():")
        users_data = User.get_all()
        print(f"Found {len(users_data)} users")
        for user_data in users_data:
            print(f"  {user_data}")
        
        # Test finding users by email
        if users_data:
            print(f"\nTesting find_by_email with first user's email...")
            first_user_email = users_data[0]['email']
            print(f"Looking for email: '{first_user_email}'")
            found_user = User.find_by_email(first_user_email)
            if found_user:
                print(f"✅ Found user: {found_user.name} ({found_user.email})")
            else:
                print("❌ User not found by email")
        
    except Exception as e:
        print(f"❌ Error testing user operations: {e}")
        import traceback
        traceback.print_exc()

def clean_database():
    """Clean all data from database"""
    print("\n🧹 CLEANING DATABASE...")
    confirmation = input("This will delete ALL data. Are you sure? (type 'yes' to confirm): ").strip().lower()
    
    if confirmation != 'yes':
        print("Cleanup cancelled.")
        return
    
    session = get_session()
    try:
        # Delete in correct order due to foreign key constraints
        deleted_transactions = session.query(Transaction).count()
        session.query(Transaction).delete()
        
        deleted_categories = session.query(Category).count()
        session.query(Category).delete()
        
        deleted_users = session.query(User).count()
        session.query(User).delete()
        
        session.commit()
        print(f"✅ Cleaned database:")
        print(f"  - Deleted {deleted_transactions} transactions")
        print(f"  - Deleted {deleted_categories} categories")
        print(f"  - Deleted {deleted_users} users")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error cleaning database: {e}")
    finally:
        session.close()

def create_test_user():
    """Create a test user to verify functionality"""
    print("\n👤 CREATING TEST USER...")
    
    try:
        user = User.create(name="Test User", email="test@example.com")
        print(f"✅ Created test user: {user.name} ({user.email})")
        
        # Verify we can find the user
        found_user = User.find_by_email("test@example.com")
        if found_user:
            print(f"✅ Successfully found user by email: {found_user.name}")
        else:
            print("❌ Could not find user by email")
            
        return user
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None

def show_menu():
    """Show debug menu options"""
    print("\n" + "="*50)
    print("🛠️  DEBUG & CLEANUP MENU")
    print("="*50)
    print("1. 🔍 Inspect Database")
    print("2. 🧪 Test User Operations")
    print("3. 👤 Create Test User")
    print("4. 🧹 Clean Database")
    print("5. 🔄 Full Reset (Clean + Create Test User)")
    print("0. 🚪 Exit")
    print("="*50)

def main():
    """Main debug script"""
    print("🛠️  Personal Finance Tracker - Debug Tool")
    
    # Create tables if they don't exist
    create_tables()
    
    while True:
        show_menu()
        choice = input("\n> ").strip()
        
        if choice == "0":
            print("Debug session ended.")
            break
        elif choice == "1":
            inspect_database()
        elif choice == "2":
            test_user_operations()
        elif choice == "3":
            create_test_user()
        elif choice == "4":
            clean_database()
        elif choice == "5":
            clean_database()
            create_test_user()
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
    