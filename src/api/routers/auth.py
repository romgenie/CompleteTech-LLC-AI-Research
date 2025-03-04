"""
Authentication router for the API.

This module provides endpoints for user authentication and token management.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from src.api.dependencies.auth import (
    User, 
    create_access_token, 
    get_current_user, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)


logger = logging.getLogger(__name__)
router = APIRouter()


class Token(BaseModel):
    """Model for an access token."""
    access_token: str
    token_type: str
    expires_at: datetime


# For demonstration purposes - replace with database in production
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": "fakehashedpassword",
        "disabled": False,
    },
    "user": {
        "username": "user",
        "full_name": "Regular User",
        "email": "user@example.com",
        "hashed_password": "fakehashedpassword",
        "disabled": False,
    },
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password
        
    Returns:
        bool: True if the password is correct, False otherwise
    """
    # This is a simplified example - use a proper password hash in production
    return plain_password == "password" and hashed_password == "fakehashedpassword"


def authenticate_user(username: str, password: str) -> Dict[str, Any]:
    """
    Authenticate a user with username and password.
    
    Args:
        username: The username
        password: The password
        
    Returns:
        Dict[str, Any]: User data if authentication succeeds
        
    Raises:
        HTTPException: If authentication fails
    """
    if username not in fake_users_db:
        return None
        
    user = fake_users_db[username]
    if not verify_password(password, user["hashed_password"]):
        return None
        
    return user


@router.post("/token", response_model=Token, summary="Get access token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, Any]:
    """
    Authenticate user and provide a JWT token.
    
    Args:
        form_data: Form with username and password
        
    Returns:
        Dict[str, Any]: Access token data
        
    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=access_token_expires
    )
    
    # Calculate expiration time
    expires_at = datetime.utcnow() + access_token_expires
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at
    }


@router.get("/users/me", response_model=User, summary="Get current user")
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get information about the current authenticated user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current user information
    """
    return current_user