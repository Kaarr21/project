# lib/helpers.py
from models.user import User
from models.category import Category
from models.transaction import Transaction
from datetime import datetime
import re

# Global variable to store current user
current_user = None

def exit_program():
    """Exit the program gracefully"""
    print("Thank you for using Personal Finance Tracker. Goodbye!")
    exit()

def validate_email(email):
    """Validate email format using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_amount(amount_str):
    """Validate and convert amount string to float"""
    try:
        amount = float(amount_str)
        if amount == 0:
            raise ValueError("Amount cannot be zero")
        return amount
    except ValueError:
        raise ValueError("Please enter a valid number")

def get_user_input(prompt, validator=None):
    """Get user input with optional validation"""
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                print("Input cannot be empty. Please try again.")
                continue
            
            if validator:
                return validator(user_input)
            return user_input
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None

# User Management Functions
def create_user():
    """Create a new user account"""
    print("\n=== Create New User ===")
    
    name = get_user_input("Enter your name: ")
    if not name:
        return
    
    email = get_user_input("Enter your email: ", validate_email)
    if not email:
        return
    
    try:
        user = User.create(name=name, email=email)
        print(f"✅ User created successfully! Welcome, {user.name}!")
        return user
    except Exception as e:
        print(f"❌ Error creating user: {e}")

def login_user():
    """Login existing user"""
    print("\n=== User Login ===")
    
    email = get_user_input("Enter your email: ")
    if not email:
        return None
    
    try:
        user = User.find_by_email(email)
        if user:
            print(f"✅ Welcome back, {user.name}!")
            return user
        else:
            print("❌ User not found. Please check your email or create a new account.")
            return None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def display_all_users():
    """Display all users in the system"""
    print("\n=== All Users ===")
    try:
        users_data = User.get_all()
        if not users_data:
            print("No users found.")
            return
        
        for user_info in users_data:
            print(f"ID: {user_info['id']} | Name: {user_info['name']} | Email: {user_info['email']}")
            print(f"  Balance: ${user_info['balance']:.2f} | Categories: {user_info['categories_count']} | Transactions: {user_info['transactions_count']}")
            print("-" * 50)
    except Exception as e:
        print(f"❌ Error retrieving users: {e}")

def delete_user():
    """Delete a user account"""
    print("\n=== Delete User ===")
    
    user_id = get_user_input("Enter user ID to delete: ", lambda x: int(x))
    if not user_id:
        return
    
    try:
        user = User.find_by_id(user_id)
        if not user:
            print("❌ User not found.")
            return
        
        confirmation = input(f"Are you sure you want to delete user '{user.name}'? This will delete all their data. (yes/no): ").strip().lower()
        if confirmation == 'yes':
            user.delete()
            print("✅ User deleted successfully.")
            # If we just deleted the current user, log them out
            global current_user
            if current_user and current_user.id == user_id:
                current_user = None
        else:
            print("Deletion cancelled.")
    except Exception as e:
        print(f"❌ Error deleting user: {e}")

# Category Management Functions
def create_category():
    """Create a new spending category"""
    if not current_user:
        print("❌ Please login first.")
        return
    
    print("\n=== Create New Category ===")
    
    name = get_user_input("Enter category name (e.g., Food, Transport, Entertainment): ")
    if not name:
        return
    
    budget_input = input("Enter budget limit for this category (optional, press Enter to skip): ").strip()
    budget_limit = 0.0
    if budget_input:
        try:
            budget_limit = float(budget_input)
            if budget_limit < 0:
                print("Budget limit cannot be negative. Setting to 0.")
                budget_limit = 0.0
        except ValueError:
            print("Invalid budget amount. Setting to 0.")
            budget_limit = 0.0
    
    try:
        category = Category.create(name=name, user_id=current_user.id, budget_limit=budget_limit)
        budget_msg = f" with budget ${budget_limit:.2f}" if budget_limit > 0 else ""
        print(f"✅ Category '{category.name}'{budget_msg} created successfully!")
    except Exception as e:
        print(f"❌ Error creating category: {e}")

def display_user_categories():
    """Display all categories for current user"""
    if not current_user:
        print("❌ Please login first.")
        return
    
    print(f"\n=== {current_user.name}'s Categories ===")
    try:
        categories = Category.find_by_user(current_user.id)
        if not categories:
            print("No categories found. Create some categories first!")
            return
        
        for category in categories:
            budget_info = ""
            if category.budget_limit > 0:
                remaining = category.remaining_budget
                status = "⚠️ OVER BUDGET" if category.is_over_budget else "✅"
                budget_info = f" | Budget: ${category.budget_limit:.2f} | Remaining: ${remaining:.2f} {status}"
            
            print(f"ID: {category.id} | Name: {category.name} | Spent: ${category.total_spent:.2f}{budget_info}")
            print(f"  Transactions: {len(category.transactions)}")
            print("-" * 70)
    except Exception as e:
        print(f"❌ Error retrieving categories: {e}")

def display_all_categories():
    """Display all categories in the system"""
    print("\n=== All Categories ===")
    try:
        categories = Category.get_all()
        if not categories:
            print("No categories found.")
            return
        
        for category in categories:
            print(f"ID: {category.id} | Name: {category.name} | User: {category.user.name}")
            print(f"  Budget: ${category.budget_limit:.2f} | Spent: ${category.total_spent:.2f}")
            print("-" * 50)
    except Exception as e:
        print(f"❌ Error retrieving categories: {e}")

def delete_category():
    """Delete a category"""
    if not current_user:
        print("❌ Please login first.")
        return
    
    print("\n=== Delete Category ===")
    display_user_categories()
    
    category_id = get_user_input("Enter category ID to delete: ", lambda x: int(x))
    if not category_id:
        return
    
    try:
        category = Category.find_by_id(category_id)
        if not category:
            print("❌ Category not found.")
            return
        
        if category.user_id != current_user.id:
            print("❌ You can only delete your own categories.")
            return
        
        confirmation = input(f"Are you sure you want to delete category '{category.name}'? This will delete all its transactions. (yes/no): ").strip().lower()
        if confirmation == 'yes':
            category.delete()
            print("✅ Category deleted successfully.")
        else:
            print("Deletion cancelled.")
    except Exception as e:
        print(f"❌ Error deleting category: {e}")

# Transaction Management Functions
def add_transaction():
    """Add a new income or expense transaction"""
    if not current_user:
        print("❌ Please login first.")
        return
    
    print("\n=== Add New Transaction ===")
    
    # Get transaction type
    print("1. Income (money received)")
    print("2. Expense (money spent)")
    choice = input("Select transaction type (1 or 2): ").strip()
    
    if choice not in ['1', '2']:
        print("❌ Invalid choice.")
        return
    
    is_income = choice == '1'
    
    # Get description
    description = get_user_input("Enter transaction description: ")
    if not description:
        return
    
    # Get amount
    amount_str = get_user_input("Enter amount (positive number): ")
    if not amount_str:
        return
    
    try:
        amount = float(amount_str)
        if amount <= 0:
            print("❌ Amount must be positive.")
            return
        
        # Convert to negative for expenses
        if not is_income:
            amount = -amount
            
    except ValueError:
        print("❌ Invalid amount.")
        return
    
    # Get category (optional for income, recommended for expenses)
    category_id = None
    if not is_income:  # For expenses, show categories
        categories = Category.find_by_user(current_user.id)
        if categories:
            print("\nAvailable categories:")
            for cat in categories:
                print(f"{cat.id}. {cat.name}")
            print("0. No category")
            
            cat_choice = input("Select category (number): ").strip()
            if cat_choice.isdigit() and int(cat_choice) > 0:
                category_id = int(cat_choice)
                # Verify category exists and belongs to user
                selected_category = next((cat for cat in categories if cat.id == category_id), None)
                if not selected_category:
                    print("❌ Invalid category selection.")
                    return
    
    try:
        transaction = Transaction.create(
            description=description,
            amount=amount,
            user_id=current_user.id,
            category_id=category_id
        )
        
        trans_type = "Income" if is_income else "Expense"
        category_name = ""
        if transaction.category:
            category_name = f" in category '{transaction.category.name}'"
        
        print(f"✅ {trans_type} of ${abs(amount):.2f}{category_name} added successfully!")
        
        # Check budget warning for expenses
        if not is_income and transaction.category and transaction.category.is_over_budget:
            print(f"⚠️  WARNING: You've exceeded your budget for '{transaction.category.name}'!")
            
    except Exception as e:
        print(f"❌ Error adding transaction: {e}")

def display_user_transactions():
    """Display all transactions for current user"""
    if not current_user:
        print("❌ Please login first.")
        return
    
    print(f"\n=== {current_user.name}'s Transaction History ===")
    try:
        transactions = Transaction.find_by_user(current_user.id)
        if not transactions:
            print("No transactions found. Add some transactions first!")
            return
        
        total_income = 0
        total_expenses = 0
        
        for transaction in transactions:
            trans_type = "📈 INCOME" if transaction.is_income else "📉 EXPENSE"
            category_name = transaction.category.name if transaction.category else "No Category"
            date_str = transaction.transaction_date.strftime("%Y-%m-%d %H:%M")
            
            print(f"ID: {transaction.id} | {trans_type} | ${transaction.formatted_amount}")
            print(f"  Description: {transaction.description}")
            print(f"  Category: {category_name} | Date: {date_str}")
            print("-" * 70)
            
            if transaction.is_income:
                total_income += transaction.amount
            else:
                total_expenses += abs(transaction.amount)
        
        print(f"\n💰 SUMMARY:")
        print(f"Total Income: ${total_income:.2f}")
        print(f"Total Expenses: ${total_expenses:.2f}")
        print(f"Net Balance: ${total_income - total_expenses:.2f}")
        
    except Exception as e:
        print(f"❌ Error retrieving transactions: {e}")

def display_category_transactions():
    """Display transactions for a specific category"""
    if not current_user:
        print("❌ Please login first.")
        return
    
    print("\n=== Category Transactions ===")
    
    # Show user's categories
    categories = Category.find_by_user(current_user.id)
    if not categories:
        print("No categories found. Create some categories first!")
        return
    
    print("Your categories:")
    for cat in categories:
        print(f"{cat.id}. {cat.name} (${cat.total_spent:.2f} spent)")
    
    category_id = get_user_input("Enter category ID: ", lambda x: int(x))
    if not category_id:
        return
    
    try:
        category = Category.find_by_id(category_id)
        if not category or category.user_id != current_user.id:
            print("❌ Category not found or doesn't belong to you.")
            return
        
        print(f"\n=== Transactions in '{category.name}' ===")
        transactions = Transaction.find_by_category(category_id)
        
        if not transactions:
            print("No transactions found in this category.")
            return
        
        total_spent = 0
        for transaction in transactions:
            date_str = transaction.transaction_date.strftime("%Y-%m-%d %H:%M")
            print(f"ID: {transaction.id} | ${transaction.formatted_amount}")
            print(f"  Description: {transaction.description}")
            print(f"  Date: {date_str}")
            print("-" * 50)
            
            if transaction.is_expense:
                total_spent += abs(transaction.amount)
        
        print(f"\nTotal spent in this category: ${total_spent:.2f}")
        if category.budget_limit > 0:
            remaining = category.remaining_budget
            print(f"Budget limit: ${category.budget_limit:.2f}")
            print(f"Remaining budget: ${remaining:.2f}")
            if category.is_over_budget:
                print("⚠️  OVER BUDGET!")
        
    except Exception as e:
        print(f"❌ Error retrieving category transactions: {e}")

def display_all_transactions():
    """Display all transactions in the system (admin function)"""
    print("\n=== All Transactions ===")
    try:
        transactions = Transaction.get_all()
        if not transactions:
            print("No transactions found.")
            return
        
        for transaction in transactions:
            trans_type = "INCOME" if transaction.is_income else "EXPENSE"
            category_name = transaction.category.name if transaction.category else "No Category"
            date_str = transaction.transaction_date.strftime("%Y-%m-%d")
            
            print(f"ID: {transaction.id} | {trans_type} | ${transaction.formatted_amount}")
            print(f"  User: {transaction.user.name} | Category: {category_name}")
            print(f"  Description: {transaction.description} | Date: {date_str}")
            print("-" * 60)
    except Exception as e:
        print(f"❌ Error retrieving transactions: {e}")

def delete_transaction():
    """Delete a transaction"""
    if not current_user:
        print("❌ Please login first.")
        return
    
    print("\n=== Delete Transaction ===")
    
    transaction_id = get_user_input("Enter transaction ID to delete: ", lambda x: int(x))
    if not transaction_id:
        return
    
    try:
        transaction = Transaction.find_by_id(transaction_id)
        if not transaction:
            print("❌ Transaction not found.")
            return
        
        if transaction.user_id != current_user.id:
            print("❌ You can only delete your own transactions.")
            return
        
        # Show transaction details
        trans_type = "Income" if transaction.is_income else "Expense"
        category_name = transaction.category.name if transaction.category else "No Category"
        print(f"\nTransaction to delete:")
        print(f"  {trans_type}: ${transaction.formatted_amount}")
        print(f"  Description: {transaction.description}")
        print(f"  Category: {category_name}")
        
        confirmation = input("Are you sure you want to delete this transaction? (yes/no): ").strip().lower()
        if confirmation == 'yes':
            transaction.delete()
            print("✅ Transaction deleted successfully.")
        else:
            print("Deletion cancelled.")
    except Exception as e:
        print(f"❌ Error deleting transaction: {e}")

def view_financial_summary():
    """Show comprehensive financial summary"""
    if not current_user:
        print("❌ Please login first.")
        return
    
    print(f"\n=== Financial Summary for {current_user.name} ===")
    
    try:
        # Overall summary
        balance = current_user.balance
        total_income = current_user.total_income
        total_expenses = current_user.total_expenses
        
        categories = Category.find_by_user(current_user.id)
        transactions = Transaction.find_by_user(current_user.id)
        
        print(f"💰 Total Income: ${total_income:.2f}")
        print(f"💸 Total Expenses: ${total_expenses:.2f}")
        print(f"💵 Net Balance: ${balance:.2f}")
        print(f"📁 Categories: {len(categories)}")
        print(f"📊 Transactions: {len(transactions)}")
        
        # Category breakdown
        if categories:
            print(f"\n📋 CATEGORY BREAKDOWN:")
            print("-" * 50)
            
            categories_with_spending = [(cat, cat.total_spent) for cat in categories if cat.total_spent > 0]
            categories_with_spending.sort(key=lambda x: x[1], reverse=True)  # Sort by spending amount
            
            for category, spent in categories_with_spending:
                budget_info = ""
                if category.budget_limit > 0:
                    percentage_used = (spent / category.budget_limit) * 100
                    status = "⚠️ OVER" if category.is_over_budget else "✅"
                    budget_info = f" | Budget: ${category.budget_limit:.2f} ({percentage_used:.1f}% used) {status}"
                
                print(f"  {category.name}: ${spent:.2f}{budget_info}")
        
        # Budget alerts
        over_budget_categories = [cat for cat in categories if cat.is_over_budget]
        if over_budget_categories:
            print(f"\n⚠️  BUDGET ALERTS:")
            for category in over_budget_categories:
                overage = category.total_spent - category.budget_limit
                print(f"  {category.name}: Over budget by ${overage:.2f}")
        
    except Exception as e:
        print(f"❌ Error generating financial summary: {e}")
        