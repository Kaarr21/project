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
        session = get_session()
        try:
            total = sum(t.amount for t in self.transactions if t.amount > 0)
            return total or 0.0
        finally:
            session.close()
    
    @property
    def total_expenses(self):
        """Calculate total expenses across all transactions"""
        session = get_session()
        try:
            total = sum(abs(t.amount) for t in self.transactions if t.amount < 0)
            return total or 0.0
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
        """Get all users"""
        session = get_session()
        try:
            return session.query(cls).all()
        finally:
            session.close()
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        session = get_session()
        try:
            return session.query(cls).filter_by(id=user_id).first()
        finally:
            session.close()
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        session = get_session()
        try:
            return session.query(cls).filter_by(email=email).first()
        finally:
            session.close()
    
    def delete(self):
        """Delete this user"""
        session = get_session()
        try:
            # The cascade="all, delete-orphan" will automatically delete
            # related categories and transactions
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            