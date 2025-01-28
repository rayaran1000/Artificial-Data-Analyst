import pandas as pd
from io import BytesIO
from typing import List
from pydantic import BaseModel
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import APIRouter, HTTPException, Depends, UploadFile
import io

from Components.Logger import logger
from Components.auth import get_current_user
from Components.feature_engineering import FeatureEngineering
from Components.feature_selection import FeatureSelection
from Components.data import users_edited_dataframe_collection

from Components.data import (fetch_and_read_github_file, upload_file_to_github, 
                             get_user_details, delete_file_from_github,
                             get_edited_dataframe_details)

router = APIRouter()

class FeatureEngineeringConfig(BaseModel):

    """
    Pydantic model for feature engineering configuration
    """

    columns: List[str]
    featureTask: str
    featureSubTask: str
    targetFeature: str

class FeatureSelectionConfig(BaseModel):

    """
    Pydantic model for feature selection configuration
    """

    columns: List[str]
    featureSubTask: str
    targetFeature: str
    
async def get_dataframe_info(dataset: pd.DataFrame):
    """
    Get basic information about the dataframe including preview rows, dimensions,
    and stored feature type information

    Args:
        dataset (pd.DataFrame): Dataframe to get information about

    Returns:
        dict: Dataframe information

    Raises:
        HTTPException: Internal server error if an error occurs during dataframe information fetching
    """

    logger.info(f"Entered get_dataframe_info")

    try:
        
        # Function to safely convert values to JSON-compatible format
        def safe_convert(val):
            if pd.isna(val) or val is None:
                return ''
            if isinstance(val, (float, int)):
                # Convert to string if the number is too large
                if abs(val) > 1e15:
                    return str(val)
                return float(val)
            return str(val)  # Convert all other types to string
        
        # Apply safe conversion to all elements in the dataframe
        safe_dataset = dataset.applymap(safe_convert)
        
        # Add column data types information
        column_types = {
            column: str(dtype) for column, dtype in dataset.dtypes.items()
        }
        
        info = {
            "topRows": safe_dataset.head(10).to_dict('records'),
            "rowCount": len(dataset),
            "columnCount": len(dataset.columns),
            "columnTypes": column_types
        }
        
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in get_dataframe_info: {str(e)}")

@router.get("/datacleaner/dataframe-info")
async def handle_dataframe_info(user_details: dict = Depends(get_current_user)):
    """
    Handle request to get dataframe information including feature types, and delete the edited dataframe information and the edited file from the database

    Args:
        user_details (dict): User details

    Returns:
        JSONResponse: Dataframe information

    Raises:
        HTTPException: Internal server error if an error occurs during dataframe information fetching
    """

    logger.info(f"Entered handle_dataframe_info")

    try:

        user_data = get_user_details(username=user_details['username'], role=user_details['role'])
        dataset = await fetch_and_read_github_file(user_data["file"], user_data["file_url"])

        info = await get_dataframe_info(dataset)

        # Delete the edited file from the database
        edited_dataframe_details = get_edited_dataframe_details(user_data['username'], user_data['role'], user_data['file'])

        if edited_dataframe_details:
            await delete_file_from_github(edited_dataframe_details['edited_file'])
            # Delete the edited dataframe information and the edited file from the database
            users_edited_dataframe_collection.delete_one({"username": user_data['username'], "role": user_data['role'], "file": user_data['file']})
        else:
            pass

        return JSONResponse(content=info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in handling dataframe info request: {str(e)}")


@router.post("/datacleaner/engineering")
async def handle_engineering_columns(
    feature_engineering_config: FeatureEngineeringConfig,
    user_details: dict = Depends(get_current_user)
):
    """
    Handle the columns selected for feature engineering

    Args:
        feature_engineering_config (FeatureEngineeringConfig): Feature engineering configuration
        user_details (dict): User details

    Returns:
        JSONResponse: Dataframe information

    Raises:
        HTTPException: Internal server error if an error occurs during feature engineering
    """

    logger.info(f"Entered handle_engineering_columns")

    try:

        feature_engineering = FeatureEngineering(user_details, engineering_columns=feature_engineering_config.columns, 
                                               target_feature=feature_engineering_config.targetFeature,
                                               featureengineeringTask=feature_engineering_config.featureTask, 
                                               featureengineeringSubTask=feature_engineering_config.featureSubTask)
        
        user_data = get_user_details(username=user_details['username'], role=user_details['role'])
        
        dataset, need_to_update = await feature_engineering.handle_dataframe(user_details)

        edited_dataset = feature_engineering.manager(dataset)

        # Convert DataFrame to CSV bytes
        csv_content = edited_dataset.to_csv(index=False).encode('utf-8')
        
        # Create a UploadFile object
        file = UploadFile(
            filename=f"edited_{user_data['file']}_file_user_{user_data['username']}.csv",
            file=BytesIO(csv_content)
        )

        # Upload to GitHub
        upload_result = await upload_file_to_github(file, user_details.get('current_file'))

        # Add information about the edited dataframe to the database
        if need_to_update:
            users_edited_dataframe_collection.insert_one({
                "username": user_data['username'],
                "role": user_data['role'],
                "file": user_data['file'],
                "edited_file": file.filename,
                "edited_file_url": upload_result["download_url"]
            })

        info = await get_dataframe_info(edited_dataset)
       
        return JSONResponse(content=info)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in updating engineering columns: {str(e)}")

@router.post("/datacleaner/selection")
async def handle_selection_columns(
    feature_selection_config: FeatureSelectionConfig,
    user_details: dict = Depends(get_current_user)
):
    """
    Handle the columns selected for feature selection

    Args:
        feature_selection_config (FeatureSelectionConfig): Feature selection configuration
        user_details (dict): User details

    Returns:
        JSONResponse: Dataframe information

    Raises:
        HTTPException: Internal server error if an error occurs during feature selection
    """

    logger.info(f"Entered handle_selection_columns")

    try:

        feature_selection = FeatureSelection(user_details, selection_columns=feature_selection_config.columns,  
                                             featureselectionSubTask=feature_selection_config.featureSubTask,target_feature=feature_selection_config.targetFeature)
        user_data = get_user_details(username=user_details['username'], role=user_details['role'])
        
        dataset, need_to_update = await feature_selection.handle_dataframe(user_details)

        edited_dataset = feature_selection.manager(dataset)

        # Convert DataFrame to CSV bytes
        csv_content = edited_dataset.to_csv(index=False).encode('utf-8')
        
        # Create a UploadFile object
        file = UploadFile(
            filename=f"edited_{user_data['file']}_file_user_{user_data['username']}.csv",
            file=BytesIO(csv_content)
        )

        # Upload to GitHub
        upload_result = await upload_file_to_github(file, user_details.get('current_file'))

        # Add information about the edited dataframe to the database
        if need_to_update:
            users_edited_dataframe_collection.insert_one({
                "username": user_data['username'],
                "role": user_data['role'],
                "file": user_data['file'],
                "edited_file": file.filename,
                "edited_file_url": upload_result["download_url"]
            })

        info = await get_dataframe_info(edited_dataset)
       
        return JSONResponse(content=info)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in updating selection columns: {str(e)}")

@router.get("/datacleaner/download")
async def download_dataframe(user_details: dict = Depends(get_current_user)):
    """
    Download the current state of the dataframe as a CSV file

    Args:
        user_details (dict): User details

    Returns:
        StreamingResponse: CSV file download

    Raises:
        HTTPException: Internal server error if an error occurs during download
    """
    
    logger.info("Entered download_dataframe")
    
    try:
        user_data = get_user_details(username=user_details['username'], role=user_details['role'])
        
        # Check if there's an edited version first
        edited_dataframe_details = get_edited_dataframe_details(
            user_data['username'], 
            user_data['role'], 
            user_data['file']
        )
        
        if edited_dataframe_details:
            dataset = await fetch_and_read_github_file(
                edited_dataframe_details['edited_file'], 
                edited_dataframe_details['edited_file_url']
            )
        else:
            dataset = await fetch_and_read_github_file(
                user_data["file"], 
                user_data["file_url"]
            )

        # Create CSV string from dataframe
        stream = io.StringIO()
        dataset.to_csv(stream, index=False)
        
        response = StreamingResponse(
            iter([stream.getvalue()]),
            media_type="text/csv",
            headers={
                'Content-Disposition': f'attachment; filename=data_export.csv'
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error downloading dataframe: {str(e)}"
        )
