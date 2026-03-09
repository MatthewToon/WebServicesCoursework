"""
Database configuration module.

This file defines the core SQLAlchemy database infrastructure used by the
FastAPI application. It is responsible for configuring the database engine,
session management, and the base class used by ORM models.

Key responsibilities:
- Load environment variables from the project's `.env` file.
- Create the SQLAlchemy engine used to communicate with PostgreSQL.
- Configure a session factory (SessionLocal) for database transactions.
- Define the declarative Base class used by all database models.
- Provide a reusable dependency (`get_db`) for FastAPI routes that ensures
  database sessions are correctly opened and closed for each request.

Separating database configuration into its own module improves code
organisation, supports dependency injection in FastAPI routes, and ensures
consistent database access throughout the application.
"""

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
load_dotenv()

# Retrieve the database connection string from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create a configured Session class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class used by SQLAlchemy ORM models
Base = declarative_base()


# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()