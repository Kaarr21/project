# lib/models/user.py
from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import relationship
from . import Base, get_session
from datetime import datetime

class User(Base):
    """
    User model represents a person using the finance tracker.
    Each user can have multiple categories and transactions.
    """
    __tablename__ = 'users'
    
    # Primary key - unique identifier for each user
    id = Column(Integer, primary_key=True)
    # User's name - required field
    name = Column(String(50), nullable=False)
    # User's email - unique constraint ensures no duplicates
    email = Column(String(100), unique=True, nullable=False)
    # When the user account was created
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships - SQLAlchemy will handle the foreign key connections
    # back_populates creates bidirectional relationships
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"
    
    # Property methods for validation and constraints
    @property
    def total_income(self):
        """Calculate total income across all transactions"""
        # Use a fresh session to avoid lazy loading issues
        session = get_session()
        try:
            from .transaction import Transaction
            total = session.query(Transaction).filter_by(user_id=self.id).filter(Transaction.amount > 0).all()
            return sum(t.amount for t in total) or 0.0
        finally:
            session.close()
    
    @property
    def total_expenses(self):
        """Calculate total expenses across all transactions"""
        # Use a fresh session to avoid lazy loading issues
        session = get_session()
        try:
            from .transaction import Transaction
            expenses = session.query(Transaction).filter_by(user_id=self.id).filter(Transaction.amount < 0).all()
            return sum(abs(t.amount) for t in expenses) or 0.0
        finally:
            session.close()
    
    @property
    def balance(self):
        """Calculate current balance (income - expenses)"""
        return self.total_income - self.total_expenses
    
    # ORM Methods (Create, Read, Update, Delete operations)
    @classmethod
    def create(cls, name, email):
        """Create a new user"""
        session = get_session()
        try:
            # Validate input
            if not name or not email:
                raise ValueError("Name and email are required")
            
            # Check if email already exists
            existing_user = session.query(cls).filter_by(email=email).first()
            if existing_user:
                raise ValueError("Email already exists")
            
            # Create new user
            user = cls(name=name, email=email)
            session.add(user)
            session.commit()
            session.refresh(user)  # Get the ID assigned by database
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def get_all(cls):
        """Get all users with their related data properly loaded"""
        session = get_session()
        try:
            # Get all users with proper data access while session is active
            users = session.query(cls).all()
            
            # Create a list of user data dictionaries with all data accessed in session
            user_data = []
            for user in users:
                # Access all needed data while session is active
                categories_count = len(user.categories) if user.categories else 0
                transactions_count = len(user.transactions) if user.transactions else 0
                balance = sum(t.amount for t in user.transactions) if user.transactions else 0.0
                
                user_info = {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,  # This was the bug - accessing after session close
                    'categories_count': categories_count,
                    'transactions_count': transactions_count,
                    'balance': balance
                }
                user_data.append(user_info)
            
            return user_data
        finally:
            session.close()
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        session = get_session()
        try:
            user = session.query(cls).filter_by(id=user_id).first()
            if user:
                # Create a detached instance with all data loaded
                detached_user = cls()
                detached_user.id = user.id
                detached_user.name = user.name
                detached_user.email = user.email
                detached_user.created_at = user.created_at
                return detached_user
            return None
        finally:
            session.close()
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        session = get_session()
        try:
            user = session.query(cls).filter_by(email=email).first()
            if user:
                # Create a detached instance with all data loaded
                detached_user = cls()
                detached_user.id = user.id
                detached_user.name = user.name
                detached_user.email = user.email
                detached_user.created_at = user.created_at
                return detached_user
            return None
        finally:
            session.close()
    
    def delete(self):
        """Delete this user"""
        session = get_session()
        try:
            # Get the user from the current session to avoid detached instance issues
            user_to_delete = session.query(User).filter_by(id=self.id).first()
            if user_to_delete:
                # The cascade="all, delete-orphan" will automatically delete
                # related categories and transactions
                session.delete(user_to_delete)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            