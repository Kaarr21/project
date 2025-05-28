# lib/cli.py
from helpers import (
    exit_program,
    create_user,
    login_user,
    display_all_users,
    delete_user,
    create_category,
    display_user_categories,
    display_all_categories,
    delete_category,
    add_transaction,
    display_user_transactions,
    display_category_transactions,
    display_all_transactions,
    delete_transaction,
    view_financial_summary,
    current_user
)
from models import create_tables

def main():
    """
    Main function that runs the CLI application.
    This uses a while loop to keep the program running until user chooses to exit.
    """
    # Create database tables if they don't exist
    create_tables()
    
    print("🏦 Welcome to Personal Finance Tracker! 🏦")
    print("Manage your income, expenses, and budgets with ease.")
    
    # Main application loop
    while True:
        show_main_menu()
        choice = input("\n> ").strip()
        
        # Handle menu choices using if-elif structure
        if choice == "0":
            exit_program()
        elif choice == "1":
            handle_user_management()
        elif choice == "2":
            handle_category_management()
        elif choice == "3":
            handle_transaction_management()
        elif choice == "4":
            view_financial_summary()
        else:
            print("❌ Invalid choice. Please select a number from the menu.")

def show_main_menu():
    """
    Display the main menu options.
    This function separates the UI display from the logic.
    """
    global current_user
    
    # Show current user status
    if current_user:
        print(f"\n👤 Logged in as: {current_user.name} ({current_user.email})")
        print(f"💰 Current Balance: ${current_user.balance:.2f}")
    else:
        print("\n👤 Not logged in")
    
    print("\n" + "="*50)
    print("🏦 PERSONAL FINANCE TRACKER - MAIN MENU")
    print("="*50)
    print("1. 👥 User Management")
    print("2. 📁 Category Management") 
    print("3. 💰 Transaction Management")
    print("4. 📊 View Financial Summary")
    print("0. 🚪 Exit")
    print("="*50)

def handle_user_management():
    """
    Handle user management submenu.
    This demonstrates nested menu structure and input validation.
    """
    while True:
        print("\n" + "="*40)
        print("👥 USER MANAGEMENT")
        print("="*40)
        print("1. 🆕 Create New User")
        print("2. 🔐 Login")
        print("3. 👁️  View All Users")
        print("4. 🗑️  Delete User")
        print("0. ⬅️  Back to Main Menu")
        print("="*40)
        
        choice = input("\n> ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            create_user()
        elif choice == "2":
            global current_user
            user = login_user()
            if user:
                current_user = user
        elif choice == "3":
            display_all_users()
        elif choice == "4":
            delete_user()
        else:
            print("❌ Invalid choice.")

def handle_category_management():
    """
    Handle category management submenu.
    This shows how we check for user authentication before allowing operations.
    """
    while True:
        print("\n" + "="*40)
        print("📁 CATEGORY MANAGEMENT")
        print("="*40)
        print("1. 🆕 Create New Category")
        print("2. 👁️  View My Categories")
        print("3. 🌐 View All Categories")
        print("4. 🗑️  Delete Category")
        print("0. ⬅️  Back to Main Menu")
        print("="*40)
        
        choice = input("\n> ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            create_category()
        elif choice == "2":
            display_user_categories()
        elif choice == "3":
            display_all_categories()
        elif choice == "4":
            delete_category()
        else:
            print("❌ Invalid choice.")

def handle_transaction_management():
    """
    Handle transaction management submenu.
    This demonstrates the most complex part of our application.
    """
    while True:
        print("\n" + "="*40)
        print("💰 TRANSACTION MANAGEMENT")
        print("="*40)
        print("1. ➕ Add New Transaction")
        print("2. 📋 View My Transactions")
        print("3. 📁 View Category Transactions")
        print("4. 🌐 View All Transactions")
        print("5. 🗑️  Delete Transaction")
        print("0. ⬅️  Back to Main Menu")
        print("="*40)
        
        choice = input("\n> ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            add_transaction()
        elif choice == "2":
            display_user_transactions()
        elif choice == "3":
            display_category_transactions()
        elif choice == "4":
            display_all_transactions()
        elif choice == "5":
            delete_transaction()
        else:
            print("❌ Invalid choice.")

# Entry point - this runs when the script is executed directly
if __name__ == "__main__":
    main()
    