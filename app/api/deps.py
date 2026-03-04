"""
API dependency definitions.

FastAPI uses a dependency injection system that allows shared resources
to be automatically created and provided to route handlers. This module
acts as a central location for dependencies used across the API layer.

Currently this file re-exports the database session dependency
(`get_db`) defined in `app.db`. Route handlers can import dependencies
from this module rather than directly from infrastructure modules.

Example usage in a route:

    from fastapi import Depends
    from sqlalchemy.orm import Session
    from app.api.deps import get_db

    @router.get("/publishers")
    def list_publishers(db: Session = Depends(get_db)):
        ...

FastAPI will:
1. Create a database session
2. Inject it into the route function
3. Automatically close the session after the request finishes

As the project grows, additional dependencies such as authentication,
pagination helpers, or request context objects can be added here.
"""

from app.db import get_db

# Import in routers as: Depends(get_db)
__all__ = ["get_db"]