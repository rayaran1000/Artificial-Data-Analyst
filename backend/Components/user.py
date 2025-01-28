# user.py - Code module to handle user authentication and authorization

import os
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import timedelta
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, status, Depends,Header

from Components.Logger import logger
from Components.database import registered_users_collection

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

from Components.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_password_hash,
    UserRole
)

router = APIRouter()


class User(BaseModel):

    """
    Pydantic model for user
    """

    username: str
    password: str
    role: UserRole = UserRole.USER

class UserRegister(BaseModel):

    """
    Pydantic model for user registration
    """

    name: str
    username: str
    email: str
    password: str

class Token(BaseModel):

    """
    Pydantic model for token
    """

    access_token: str
    token_type: str


@router.post("/register", response_model=dict)
async def register(
    user: UserRegister, 
    admin_key: str = Header(None, alias="X-Admin-Key")
    ) -> dict:
    """
    Register a new user in the system.

    Args:
        user (UserRegister): User registration details
        admin_key (Optional[str]): Admin key for elevated privileges

    Returns:
        Dict: Registration confirmation message and user ID

    Raises:
        HTTPException: If username already exists or registration fails
    """
    logger.info(f"Attempting to register new user: {user.username}")

    try:

        if registered_users_collection.find_one({"username": user.username}): # Username already present in db
            raise HTTPException(status_code=400, detail="Username already registered")
        
        hashed_password = get_password_hash(user.password) # password hash generated
        # Dictionary created for the new user which stores the hashed password with key as original password, role as key and value as user or admin, then the data stored in users collection
        user_dict = user.dict()
        user_dict["name"] = user.username
        user_dict["password"] = hashed_password 

        if admin_key and admin_key == SECRET_KEY:
            user_dict["role"] = UserRole.ADMIN
        else:
            user_dict["role"] = UserRole.USER
        
        result = registered_users_collection.insert_one(user_dict)
        return {"message": "User registered successfully", "id": str(result.inserted_id)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering user: {str(e)}")


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
    ):
    """
    Authenticate user and provide access token.

    Args:
        form_data (OAuth2PasswordRequestForm): Login credentials

    Returns:
        Dict: Access token and token type

    Raises:
        HTTPException: If authentication fails
    """
    logger.info(f"Entered in 'login_for_access_token' function")

    try:

        user = authenticate_user(form_data.username, form_data.password) # Checking whether the user is present in db or not
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Generate Access Tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "role": user["role"]},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging in user: {str(e)}")

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
    ):
    """
    Authenticate user and provide access token.

    Args:
        form_data (OAuth2PasswordRequestForm): Login credentials

    Returns:
        Dict: Access token and token type

    Raises:
        HTTPException: If authentication fails
    """

    logger.info(f"Entered in 'login_for_access_token' function")

    try:

        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "role": user["role"]}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")