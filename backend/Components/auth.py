import os
import jwt
from enum import Enum
from typing import Optional
from dotenv import load_dotenv
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from Components.Logger import logger
from Components.database import registered_users_collection

load_dotenv()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set in environment variables")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 120

class UserRole(str, Enum):

    """
    Enum for the user roles : USER and ADMIN
    """

    USER = "user" 
    ADMIN = "admin"

"""
Password hashing context
"""
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

"""
OAuth2 password bearer scheme
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password: str, 
                    hashed_password: str
                    ) -> bool:
    
    """
    Verifies the password
    """

    logger.info(f"Entered in 'verify_password' function")
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    
    """
    Hashes the password
    """

    logger.info(f"Entered in 'get_password_hash' function")
    return pwd_context.hash(password)

def authenticate_user(username: str, 
                      password: str
                      ) -> dict:
    
    """
    Authenticates the user
    """

    logger.info(f"Entered in 'authenticate_user' function")
    user = registered_users_collection.find_one({"username": username})
    if not user or not verify_password(password, user["password"]):
        return False
    return user

def create_access_token(data: dict, 
                        expires_delta: Optional[timedelta] = None
                        ) -> str:
    
    """
    Creates the access token
    """

    logger.info(f"Entered in 'create_access_token' function")
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    
    """
    Gets the current user
    """

    logger.info(f"Entered in 'get_current_user' function")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = registered_users_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return {"username": user["username"], "role": user["role"]}

def admin_required(current_user: dict = Depends(get_current_user)) -> dict:
    
    """
    Checks if the user is an admin
    """

    logger.info(f"Entered in 'admin_required' function")
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

