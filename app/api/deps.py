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

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from jose import JWTError

from app.db import SessionLocal
from app.core.security import decode_token
from app.models.user import User

# Import in routers as: Depends(get_db)
__all__ = ["get_db"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
