import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status, Header, File, UploadFile, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import BaseModel, Field, ValidationError
from Components.Logger import logger
from Components.user import router as user_router
from Components.datacontrol import router as datacontrol_router
from Components.datasummarizer import router as datasummarizer_router
from Components.dashboard_visualize import router as dashboard_visualize_router
from Components.datacleaner import router as datacleaner_router
from Components.auth import (
    UserRole
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Content-Disposition"]
)

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(datacontrol_router, tags=["datacontrol"])
app.include_router(datasummarizer_router, tags=["datasummarizer"])
app.include_router(dashboard_visualize_router,tags=["visualize"])
app.include_router(datacleaner_router, tags=["datacleaner"])

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class User(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.USER

class Token(BaseModel):
    access_token: str
    token_type: str

class UserRegister(BaseModel):
    name: str
    username: str
    email: str
    password: str

class DataControlRequest(BaseModel):
    api_link: Optional[str] = Field(None, description="API link")
    aws_access_key_id: Optional[str] = Field(None, description="AWS Access Key ID")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS Secret Access Key")
    aws_region: Optional[str] = Field(None, description="AWS Region")
    gcp_project_id: Optional[str] = Field(None, description="GCP Project ID")
    gcp_service_account_key: Optional[str] = Field(None, description="GCP Service Account Key")

# Start the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
