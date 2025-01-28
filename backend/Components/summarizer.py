import os
from dotenv import load_dotenv
from fastapi import  HTTPException
from lida import Manager, TextGenerationConfig, llm

from Components.Logger import logger
from Components.data import user_secrets_collection, fetch_and_read_github_file


load_dotenv()

async def data_summarization(
        selected_method_label: str, 
        temperature: float, 
        user_details: dict
        ) -> str:
    try:

        """
        Summarize the dataset using the selected method label and temperature.

        Args:
            selected_method_label (str): The method label for summarization
            temperature (float): The temperature for summarization
            user_details (dict): User details including username and role

        Returns:
            str: The summary of the dataset

        Raises:
            HTTPException: If an unexpected error occurs
        """

        logger.info(f"Entered in 'data_summarization' function")

        # Initialize summary as empty string
        summary = ""

        model_name = os.getenv("MODEL_NAME")

        # Configure the LLM text generation with the loaded model
        text_gen = llm(provider=os.getenv("PROVIDER"), model=model_name)

        # Fetch user data from database
        user_record = user_secrets_collection.find_one({"username": user_details["username"], "role": user_details["role"]})

        # Load the dataset
        selected_dataset = await fetch_and_read_github_file(user_record["file"], user_record["file_url"])
        
        # Check if the dataset is not empty and method label is provided
        if (not selected_dataset.empty) and selected_method_label:
            # Initialize LIDA Manager with the model
            lida = Manager(text_gen=text_gen)
            textgen_config = TextGenerationConfig(
                n=1,
                temperature=temperature,
                use_cache=True,
                model=model_name              
            )

            # Perform summarization
            summary = lida.summarize(
                selected_dataset,
                summary_method=selected_method_label,
                textgen_config=textgen_config
            )

            return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in data summarization: {str(e)}")
