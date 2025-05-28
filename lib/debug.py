# lib/debug.py
"""
Debug script for testing database operations and relationships.
This file helps you test your models without going through the CLI.
"""

from models import create_tables, get_session
from models.user import User
from models.category import Category
from models.transaction import Transaction

def test_database_operations():
    """Test basic database operations"""
    print("🧪 Testing Database Operations...")
    
    # Create tables
    create_tables()
    print("✅ Tables created")
    
    try:
        # Test User creation
        print("\n📝 Testing User Operations...")
        user = User.create(name="Test User", email="test@example.com")
        print(f"✅ Created user: {user}")
        
        # Test Category creation
        print("\n📁 Testing Category Operations...")
        food_category = Category.create(name="Food", user_id=user.id, budget_limit=500.0)
        transport_category = Category.create(name="Transport", user_id=user.id, budget_limit=200.0)
        print(f"✅ Created categories: {food_category}, {transport_category}")
        
        # Test Transaction creation
        print("\n💰 Testing Transaction Operations...")
        # Add some income
        income = Transaction.create(
            description="Salary",
            amount=2000.0,
            user_id=user.id
        )
        print(f"✅ Created income: {income}")
        
        # Add some expenses
        expense1 = Transaction.create(
            description="Grocery shopping",
            amount=-150.0,
            user_id=user.id,
            category_id=food_category.id
        )
        
        expense2 = Transaction.create(
            description="Bus fare",
            amount=-25.0,
            user_id=user.id,
            category_id=transport_category.id
        )
        print(f"✅ Created expenses: {expense1}, {expense2}")
        
        # Test relationships and properties
        print("\n🔗 Testing Relationships...")
        print(f"User balance: ${user.balance:.2f}")
        print(f"User total income: ${user.total_income:.2f}")
        print(f"User total expenses: ${user.total_expenses:.2f}")
        print(f"Food category spent: ${food_category.total_spent:.2f}")
        print(f"Food category remaining budget: ${food_category.remaining_budget:.2f}")
        
        # Test queries
        print("\n🔍 Testing Queries...")
        all_users = User.get_all()
        print(f"Total users: {len(all_users)}")
        
        user_categories = Category.find_by_user(user.id)
        print(f"User categories: {len(user_categories)}")
        
        user_transactions = Transaction.find_by_user(user.id)
        print(f"User transactions: {len(user_transactions)}")
        
        category_transactions = Transaction.find_by_category(food_category.id)
        print(f"Food category transactions: {len(category_transactions)}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def clean_database():
    """Clean all data from database (useful for testing)"""
    print("🧹 Cleaning database...")
    session = get_session()
    try:
        # Delete in correct order due to foreign key constraints
        session.query(Transaction).delete()
        session.query(Category).delete()
        session.query(User).delete()
        session.commit()
        print("✅ Database cleaned")
    except Exception as e:
        session.rollback()
        print(f"❌ Error cleaning database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Run tests
    test_database_operations()
    