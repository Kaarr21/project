# lib/models/category.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from . import Base, get_session

class Category(Base):
    """
    Category model represents spending categories like 'Food', 'Transport', etc.
    Each category belongs to a user and can have multiple transactions.
    """
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    # Optional budget limit for this category
    budget_limit = Column(Float, default=0.0)
    # Foreign key to link this category to a user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, budget_limit={self.budget_limit})>"
    
    @property
    def total_spent(self):
        """Calculate total amount spent in this category"""
        return sum(abs(t.amount) for t in self.transactions if t.amount < 0)
    
    @property
    def remaining_budget(self):
        """Calculate remaining budget for this category"""
        if self.budget_limit <= 0:
            return None  # No budget set
        return self.budget_limit - self.total_spent
    
    @property
    def is_over_budget(self):
        """Check if spending exceeds budget"""
        if self.budget_limit <= 0:
            return False  # No budget set
        return self.total_spent > self.budget_limit
    
    # ORM Methods
    @classmethod
    def create(cls, name, user_id, budget_limit=0.0):
        """Create a new category"""
        session = get_session()
        try:
            if not name:
                raise ValueError("Category name is required")
            
            # Verify user exists
            from .user import User
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                raise ValueError("User not found")
            
            category = cls(name=name, user_id=user_id, budget_limit=budget_limit)
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def get_all(cls):
        """Get all categories"""
        session = get_session()
        try:
            return session.query(cls).all()
        finally:
            session.close()
    
    @classmethod
    def find_by_id(cls, category_id):
        """Find category by ID"""
        session = get_session()
        try:
            return session.query(cls).filter_by(id=category_id).first()
        finally:
            session.close()
    
    @classmethod
    def find_by_user(cls, user_id):
        """Find all categories for a user"""
        session = get_session()
        try:
            return session.query(cls).filter_by(user_id=user_id).all()
        finally:
            session.close()
    
    def delete(self):
        """Delete this category"""
        session = get_session()
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            