from pymongo import MongoClient
from dotenv import load_dotenv
from Components.Logger import logger
import os
import certifi

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

try:
    client = MongoClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    client.server_info()  # Will raise exception if connection fails
    db = client['AI_Business_Analyst']
    
    # Collections
    registered_users_collection = db['registered_users']
    user_secrets_collection = db['user_data_secrets']
    users_edited_dataframe_collection = db['users_edited_dataframe']
    users_goals_collection = db['users_generated_goals']
    users_visual_code_collection = db['users_generated_visual_code_collection']

except Exception as e:
    logger.critical(f"Failed to connect to MongoDB: {str(e)}")
    raise
