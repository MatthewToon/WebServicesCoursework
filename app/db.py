import os

# dotenv allows environment variables defined in the .env file
# to be loaded into the application environment.
from dotenv import load_dotenv

# SQLAlchemy engine handles database connections
from sqlalchemy import create_engine

# sessionmaker is used to create database sessions
# declarative_base is used as the base class for ORM models
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from the .env file
# This allows sensitive configuration (e.g. database credentials)
# to be stored outside the source code.
load_dotenv()

# Retrieve the database connection string from environment variables
# Example format:
# postgresql+psycopg://user:password@localhost:5432/database
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the SQLAlchemy engine which manages the connection pool
# between the FastAPI application and PostgreSQL.
# pool_pre_ping=True ensures stale connections are checked
# before being reused from the pool.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create a configured "Session" class.
# Each session represents a transactional connection to the database.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class used by SQLAlchemy ORM models.
# All database table models will inherit from this class.
Base = declarative_base()


# Dependency for FastAPI routes
# This function provides a database session to API endpoints
# and ensures that the session is properly closed afterwards.
def get_db():
    db = SessionLocal()
    try:
        # Provide the session to the route handler
        yield db
    finally:
        # Always close the session after the request finishes
        db.close()