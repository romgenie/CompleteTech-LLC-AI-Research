"""
Authentication and authorization dependencies for the API.

This module provides dependency injection functions for user authentication
and authorization using JSON Web Tokens (JWT).
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


# Authentication configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "30"))


class User(BaseModel):
    """User model for authentication and authorization."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class TokenData(BaseModel):
    """Data contained in a JWT token."""
    username: Optional[str] = None
    exp: Optional[datetime] = None


# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with optional expiration.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """
    Decode a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        TokenData: Decoded token data
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        exp: datetime = datetime.fromtimestamp(payload.get("exp"))
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token_data = TokenData(username=username, exp=exp)
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current user based on the JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        User: The current user
        
    Raises:
        HTTPException: If the token is invalid or user is not found
    """
    token_data = decode_token(token)
    
    # In a production environment, you would query the user from a database
    # For demonstration purposes, we'll create a fake user
    user = User(
        username=token_data.username,
        email=f"{token_data.username}@example.com",
        full_name=f"{token_data.username.capitalize()} User",
        disabled=False,
    )
    
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user