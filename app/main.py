# Main FastAPI application entry point.

# This file defines the API instance and registers basic health and
# database connectivity endpoints used during development. These
# endpoints help verify that the service and database are functioning
# correctly before implementing the full API functionality.

# FastAPI is the web framework used to build the API service
from fastapi import FastAPI

# SQLAlchemy text() allows execution of raw SQL statements
from sqlalchemy import text

# Import the database engine configured in db.py
# The engine manages connections between the API and PostgreSQL
from app.db import engine

# Create the FastAPI application instance.
# This object is the main entry point for the web service and is
# used by Uvicorn to run the API server.
app = FastAPI(title="Game Publisher Intelligence API")

# Simple health check endpoint.
# This confirms that the FastAPI application itself is running.
# It does not check database connectivity.
@app.get("/health")
def health():
    return {"status": "ok"}

# Database connectivity test endpoint.
# This endpoint attempts to open a connection to the PostgreSQL
# database and execute a minimal query (SELECT 1).
#
# If this endpoint succeeds, it confirms:
# - the database container is running
# - credentials are correct
# - SQLAlchemy is configured properly
# - the API can communicate with PostgreSQL
@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar_one()

    return {
        "database": "connected",
        "test_query": result
    }