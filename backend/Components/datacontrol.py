# datacontrol.py - Code module to handle data control functionality

import requests
from typing import Optional
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form

from Components.Logger import logger
from Components.auth import get_current_user
from Components.data import (get_user_details, update_user_details, 
                             upload_file_to_github, create_user_record)


router = APIRouter()

class DataControlRequest(BaseModel):

    """
    Pydantic model for data control request
    """

    api_link: Optional[str] = Field(None, description="API link")
    aws_access_key_id: Optional[str] = Field(None, description="AWS Access Key ID")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS Secret Access Key")
    aws_region: Optional[str] = Field(None, description="AWS Region")
    gcp_project_id: Optional[str] = Field(None, description="GCP Project ID")
    gcp_service_account_key: Optional[str] = Field(None, description="GCP Service Account Key")

@router.get("/datacontrol/get")
async def handle_data_control( user_details: dict = Depends(get_current_user)):
    """
    Handle data control fetching data from database

    Args:
        user_details (dict): User details

    Returns:
        JSONResponse: Data control response

    Raises:
        HTTPException: Internal server error if an error occurs during data control fetching
    """

    logger.info(f"Entered data control get")

    try:

        user_data = get_user_details(user_details["username"],user_details["role"]) # Fetch data from database           

        return {
                "apiLink": user_data['apiLink'],
                "awsaccesskeyID": user_data['aws_access_key_ID'],
                "awsaccesskey": user_data['aws_access_key'],
                "awsregion": user_data['aws_region'],
                "gcpprojectID": user_data['gcp_project_ID'],
                "gcpaccountkey": user_data['gcp_account_key'],
                "file": user_data['file'],
                "file_url": user_data['file_url']
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in data control get: {str(e)}")

@router.post("/datacontrol/create")
async def handle_data_control(current_user: dict = Depends(get_current_user)):
    """
    Handle data control null record create in database

    Args:
        current_user (dict): Current user details

    Returns:
        JSONResponse: Data control response

    Raises:
        HTTPException: Internal server error if an error occurs during data control creation
    """

    logger.info(f"Entered data create")

    try:

        # Create or get user record in database
        user_data = create_user_record(current_user["username"], current_user["role"])

        return {
            "apiLink": user_data['apiLink'],
            "awsaccesskeyID": user_data['aws_access_key_ID'],
            "awsaccesskey": user_data['aws_access_key'],
            "awsregion": user_data['aws_region'],
            "gcpprojectID": user_data['gcp_project_ID'],
            "gcpaccountkey": user_data['gcp_account_key'],
            "file": user_data['file'],
            "file_url": user_data['file_url']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in data control create: {str(e)}")

@router.put("/datacontrol/update")
async def update_user_data(
    apiLink: str = Form(...),
    aws_access_key_ID: str = Form(None),
    aws_access_key: str = Form(None),
    aws_region: str = Form(None),
    gcp_account_key: str = Form(None),
    gcp_project_ID: str = Form(None),
    file: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Handle data control updation in database

    Args:
        apiLink (str): API link
        aws_access_key_ID (str): AWS Access Key ID
        aws_access_key (str): AWS Secret Access Key
        aws_region (str): AWS Region
        gcp_account_key (str): GCP Service Account Key
        gcp_project_ID (str): GCP Project ID
        file (UploadFile): File to upload
        current_user (dict): Current user details

    Returns:
        JSONResponse: Data control response

    Raises:
        HTTPException: Internal server error if an error occurs during data control updation
    """

    logger.info(f"Entered data control update")

    try:

        current_user_details = get_user_details(current_user["username"],current_user["role"])
        update_data = {}

        # Check and update api Link
        if apiLink is not None and apiLink != current_user_details["apiLink"]:
            update_data["apiLink"] = apiLink

        # Check and update aws_access_key_ID
        if aws_access_key_ID is not None and aws_access_key_ID != current_user_details["aws_access_key_ID"]:
            update_data["aws_access_key_ID"] = aws_access_key_ID

        # Check and update aws_access_key
        if aws_access_key is not None and aws_access_key != current_user_details["aws_access_key"]:
            update_data["aws_access_key"] = aws_access_key

        # Check and update aws_region
        if aws_region is not None and aws_region != current_user_details["aws_region"]:
            update_data["aws_region"] = aws_region

        # Check and update gcp_account_key
        if gcp_account_key is not None and gcp_account_key != current_user_details["gcp_account_key"]:
            update_data["gcp_account_key"] = gcp_account_key

        # Check and update gcp_project_ID
        if gcp_project_ID is not None and gcp_project_ID != current_user_details["gcp_project_ID"]:
            update_data["gcp_project_ID"] = gcp_project_ID
        
        update_data["role"] = current_user["role"]

        if file:
            upload_result = await upload_file_to_github(file)
            update_data["file"] = upload_result["file_name"]  # Store the actual filename
            update_data["file_url"] = upload_result["download_url"]  # Store the GitHub link

        result = update_user_details(current_user["username"],update_data)
        
        if result:
            return JSONResponse(content={"message": "User data updated successfully"})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in data control update: {str(e)}")

@router.get("/datacontrol/download")
async def download_file(current_user: dict = Depends(get_current_user)):
    """
    Handle data control file download from GitHub

    Args:
        current_user (dict): Current user details

    Returns:
        StreamingResponse: Data control response

    Raises:
        HTTPException: Internal server error if an error occurs during data control file download
    """

    logger.info(f"Entered data control download")

    try:

        # Fetch the GitHub URL from your database based on the current user
        user_details = get_user_details(current_user["username"],current_user["role"])  # Fetching data from database
        
        # Make a request to GitHub
        response = requests.get(user_details["file_url"], stream=True)
        response.raise_for_status()
       
        # Return a StreamingResponse
        return StreamingResponse(
            response.iter_content(chunk_size=8192),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{user_details["file"]}"'
            }
        )
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error in data control download: {str(e)}")