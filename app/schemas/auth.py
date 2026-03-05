"""
Authentication schemas.

Defines request/response shapes for user registration and token responses.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 characters recommended.")
    display_name: str | None = Field(default=None, max_length=80)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"