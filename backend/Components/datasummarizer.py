# datasummarizer.py - Code module to handle data summarization functionality using LIDA

import numpy as np
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Depends

from Components.Logger import logger
from Components.auth import get_current_user
from Components.summarizer import data_summarization


router = APIRouter()

class DataSummarizationRequest(BaseModel):

    """
    Pydantic model for data summarization request
    """

    selected_method: str
    temperature: float

def sanitize_summary(data):

    """
    Sanitize the summary data to remove NaN or infinite values
    """

    logger.info(f"Sanitizing the summary data: {data}")

    try:

        if isinstance(data, dict):
            # Recursively sanitize each item in a dictionary
            return {k: sanitize_summary(v) for k, v in data.items()}
        elif isinstance(data, list):
            # Recursively sanitize each item in a list
            return [sanitize_summary(item) for item in data]
        elif isinstance(data, (int, float)):  # Only check numeric types
            # Replace NaN or infinite values with None
            return data if np.isfinite(data) else None
        else:
            # Return the item as is if it's not a number
            return data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in sanitizing the summary data: {str(e)}")
    
# Data Summarization Post
@router.post("/datasummarizer")
async def handle_data_control(request: DataSummarizationRequest, 
                              user_details: dict = Depends(get_current_user)
                              ):
    """
    Handle data summarization using LIDA

    Args:
        request (DataSummarizationRequest): Data summarization request
        user_details (dict): User details

    Returns:
        JSONResponse: Data summarization response

    Raises:
        HTTPException: Internal server error if an error occurs during data summarization
    """
    
    logger.info(f"Handling data summarization request: {request}")

    try:

        if request.selected_method == "llm-enriched":
            # Use LLM to generate a more enriched summary
            selected_method_label = "llm"
        elif request.selected_method == "default":
            # Generate a default summary based on statistics
            selected_method_label = "default"
        elif request.selected_method == "column-names-only":
            # Generate a simple summary based on column names
            selected_method_label = "columns"
        else:
        # Raise an exception if `selected_method` is not valid
            raise ValueError("Invalid selected method provided." , request.selected_method)

        summary = await data_summarization(selected_method_label, request.temperature , user_details)

        sanitized_summary = sanitize_summary(summary)

        return JSONResponse(content={"summary": sanitized_summary})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in handling data summarization: {str(e)}")