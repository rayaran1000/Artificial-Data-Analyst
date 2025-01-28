import os
import httpx
import base64
import requests
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile

from Components.Logger import logger
from Components.database import user_secrets_collection, users_edited_dataframe_collection

load_dotenv()

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Secret details    
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set in environment variables")
ALGORITHM = os.getenv("ALGORITHM")

def get_user_details(username,
                     role
                     ):
    """
    Get user details from the database
    """

    logger.info(f"Entered get_user_details with username: {username} and role: {role}")

    try:    
        user_details = user_secrets_collection.find_one({"username": username, "role": role})
        logger.info("Entered user details")

        if not user_details:
            raise HTTPException(status_code=404, detail="User not found")
        return user_details
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in getting user details: {str(e)}")

def get_edited_dataframe_details(username,
                                 role,
                                 file
                                 ):
    """
    Get edited dataframe details from the database
    """

    try:
        edited_dataframe_details = users_edited_dataframe_collection.find_one({"username": username, "role": role, "file": file})
        logger.info(f"Edited dataframe details: {edited_dataframe_details}")

        if not edited_dataframe_details:
            return None
    
        return edited_dataframe_details
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in getting edited dataframe details: {str(e)}")

def create_user_record(username, 
                       role
                       ):
    """
    Create a user record in the database
    """

    try:
        # Check if user already exists
        existing_user = user_secrets_collection.find_one({"username": username, "role": role})
        if existing_user:
            return existing_user  # User already exists, return the existing record

        # Create new user record
        new_user = {
            "username": username,
            "role": role,
            "apiLink": None,
            "aws_access_key": None,
            "aws_access_key_ID": None,
            "aws_region": None,
            "cloud_service": None,
            "gcp_account_key": None,
            "gcp_project_ID": None,
            "file": None,
            "file_url": None
        }
        
        result = user_secrets_collection.insert_one(new_user)
        
        if result.inserted_id:
            return user_secrets_collection.find_one({"_id": result.inserted_id})
        else:
            raise HTTPException(status_code=500, detail="Failed to create user record")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while creating the user record: {str(e)}")

def update_user_details(username,
                        update_data
                        ):
    """
    Update user details in the database
    """

    logger.info("Updating user details")

    try:
        result = user_secrets_collection.update_one(
        {"username": username, "role": update_data["role"]},
        {"$set": update_data}
    )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="No data updated")

        return 'Data updated successfully'
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in updating user details: {str(e)}")

async def upload_file_to_github(file: UploadFile, 
                                current_file: str = None
                                ):
    """
    Upload a file to GitHub
    """

    logger.info("Uploading file to GitHub")

    try:

        # Validate file type
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            raise HTTPException(status_code=400, detail="File must be a CSV or XLSX format.")

        # GitHub API URL for uploading the new file
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{file.filename}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

        # Read the file content
        file_content = await file.read()
        encoded_content = base64.b64encode(file_content).decode('utf-8')

        async with httpx.AsyncClient() as client:
            # Check if the new file is the same as the current file
            if current_file and current_file == file.filename:
                raise HTTPException(status_code=400, detail="Similar file already in use")

            # Check if the new file already exists in the repo
            response = await client.get(url, headers=headers)

            if response.status_code == 200:  # File exists
                existing_file_info = response.json()
                sha = existing_file_info['sha']

                # If it's a different file, delete the old one first
                if current_file and current_file != file.filename:
                    delete_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{current_file}"
                    delete_data = {
                        "message": f"Remove old file {current_file}",
                        "sha": sha
                    }

                    delete_response = await client.delete(delete_url, headers=headers, json=delete_data)

                    if delete_response.status_code != 200:
                        raise HTTPException(status_code=500, detail=f"Failed to delete old file: {delete_response.text}")

                # Prepare to update the existing file
                upload_data = {
                    "message": f"Update {file.filename}",
                    "content": encoded_content,
                    "sha": sha
                }
            else:
                # File doesn't exist, prepare to create a new file
                upload_data = {
                    "message": f"Add {file.filename}",
                    "content": encoded_content
                }

            # Upload/update the file
            upload_response = await client.put(url, headers=headers, json=upload_data)

            if upload_response.status_code not in (201, 200):
                raise HTTPException(status_code=500, detail=f"GitHub upload failed: {upload_response.text}")

            # Retrieve the download URL
            download_url = upload_response.json()["content"]["download_url"]

            # Return both the file name and the GitHub download URL
            return {
                "file_name": file.filename,
                "download_url": download_url
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in uploading file to GitHub: {str(e)}")

async def fetch_and_read_github_file(filename,
                                     file_url
                                     ):
    """
    Fetch and read a file from GitHub
    """

    try:
        # Make a request to GitHub to get the file
        response = requests.get(file_url)
        response.raise_for_status()
    
        # Get the file extension (CSV or XLSX)
        file_extension = filename.split('.')[-1].lower()
    
        # Read the file content into a pandas DataFrame based on the file type
        if file_extension == 'csv':
            # Read CSV file
            file_content = pd.read_csv(BytesIO(response.content))
        elif file_extension == 'xlsx':
            # Read Excel file
            file_content = pd.read_excel(BytesIO(response.content))
        else:
            raise ValueError("Unsupported file format. Only CSV and XLSX are supported.")
    
        # Return the DataFrame for further use
        return file_content
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in fetching and reading GitHub file: {str(e)}")

async def delete_file_from_github(file_name: str):
    """
    Delete a file from GitHub
    """

    logger.info(f"Deleting file {file_name} from GitHub")

    try:

        # GitHub API URL for deleting the file
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{file_name}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

        async with httpx.AsyncClient() as client:
            # Get the file's SHA to delete it
            response = await client.get(url, headers=headers)

            if response.status_code == 200:  # File exists
                file_info = response.json()
                sha = file_info['sha']

                # Prepare the delete request
                delete_data = {
                    "message": f"Delete {file_name}",
                    "sha": sha
                }

                # Send the delete request using request() method instead
                delete_response = await client.request(
                    "DELETE",
                    url,
                    headers=headers,
                    json=delete_data
                )

                if delete_response.status_code == 200:
                    logger.info(f"File {file_name} deleted successfully")
                    return {"message": f"File {file_name} deleted successfully"}
                else:
                    raise HTTPException(status_code=500, detail=f"Failed to delete file: {delete_response.text}")
            else:
                raise HTTPException(status_code=404, detail="File not found on GitHub")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in deleting file from GitHub: {str(e)}")

