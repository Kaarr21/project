# lib/models/transaction.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from . import Base, get_session
from datetime import datetime

class Transaction(Base):
    """
    Transaction model represents individual financial transactions.
    Each transaction belongs to a user and optionally to a category.
    Positive amounts are income, negative amounts are expenses.
    """
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    description = Column(String(200), nullable=False)
    # Positive for income, negative for expenses
    amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, description={self.description}, amount={self.amount})>"
    
    @property
    def is_income(self):
        """Check if this is an income transaction"""
        return self.amount > 0
    
    @property
    def is_expense(self):
        """Check if this is an expense transaction"""
        return self.amount < 0
    
    @property
    def formatted_amount(self):
        """Return formatted amount with currency symbol"""
        return f"${abs(self.amount):.2f}"
    
    # ORM Methods
    @classmethod
    def create(cls, description, amount, user_id, category_id=None, transaction_date=None):
        """Create a new transaction"""
        session = get_session()
        try:
            if not description:
                raise ValueError("Description is required")
            if amount == 0:
                raise ValueError("Amount cannot be zero")
            
            # Verify user exists
            from .user import User
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Verify category exists (if provided)
            if category_id:
                from .category import Category
                category = session.query(Category).filter_by(id=category_id).first()
                if not category:
                    raise ValueError("Category not found")
                if category.user_id != user_id:
                    raise ValueError("Category does not belong to this user")
            
            transaction = cls(
                description=description,
                amount=amount,
                user_id=user_id,
                category_id=category_id,
                transaction_date=transaction_date or datetime.now()
            )
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            return transaction
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def get_all(cls):
        """Get all transactions"""
        session = get_session()
        try:
            return session.query(cls).order_by(cls.transaction_date.desc()).all()
        finally:
            session.close()
    
    @classmethod
    def find_by_id(cls, transaction_id):
        """Find transaction by ID"""
        session = get_session()
        try:
            return session.query(cls).filter_by(id=transaction_id).first()
        finally:
            session.close()
    
    @classmethod
    def find_by_user(cls, user_id):
        """Find all transactions for a user"""
        session = get_session()
        try:
            return session.query(cls).filter_by(user_id=user_id).order_by(cls.transaction_date.desc()).all()
        finally:
            session.close()
    
    @classmethod
    def find_by_category(cls, category_id):
        """Find all transactions for a category"""
        session = get_session()
        try:
            return session.query(cls).filter_by(category_id=category_id).order_by(cls.transaction_date.desc()).all()
        finally:
            session.close()
    
    def delete(self):
        """Delete this transaction"""
        session = get_session()
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            