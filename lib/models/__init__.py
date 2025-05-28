# lib/models/__init__.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create database engine - using SQLite for simplicity
# The database file will be created in the current directory
engine = create_engine('sqlite:///finance_tracker.db')

# Create a base class for all our models to inherit from
# This gives them common functionality like table creation
Base = declarative_base()

# Create a session factory - this is how we'll interact with the database
# Sessions handle transactions and keep track of changes
SessionLocal = sessionmaker(bind=engine)

# Function to create all tables defined by our models
def create_tables():
    Base.metadata.create_all(engine)

# Function to get a database session
def get_session():
    return SessionLocal()
    