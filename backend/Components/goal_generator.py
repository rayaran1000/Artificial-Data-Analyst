from fastapi.responses import JSONResponse
from fastapi import HTTPException, Depends

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams.update({
    'figure.figsize': [10, 6],
    'figure.autolayout': True,
    'figure.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0,
    'savefig.transparent': True
})

from lida import Manager, TextGenerationConfig, llm
from lida.datamodel import Goal

from Components.Logger import logger
from Components.summarizer import data_summarization
from Components.data import get_user_details
from Components.database import users_goals_collection


class GoalGeneration:
    """
    Handles Goal related functionalities
    """

    def __init__(self):

        self.model_name = "llama3-70b-8192"
        self.text_gen = llm(provider="chatgroq", model=self.model_name)
        self.lida = Manager(text_gen=self.text_gen)
        self.textgen_config = TextGenerationConfig(n=1,temperature=0.5,use_cache=True,model=self.model_name)
        
    
    async def goal_generator(self, goals_count, user_data):

        """
        Generates goals for the given user as per dataset
        
        Args:
            goals_count (GoalGenerationRequest): Goals count
            user_data (dict): User data

        Returns:
            JSONResponse: Goals
        
        Raises:
            HTTPException: Internal server error if an error occurs during goal generation
        """

        logger.info(f"Entered goal generator with goals count: {goals_count} and user data: {user_data}")

        try:

            # Extract user-specific details
            username = user_data['username']
            file_name = user_data['file']

            existing_goals = users_goals_collection.find_one({"user_name": user_data['username'], "file_name": user_data['file']})

            if existing_goals:
                summary = existing_goals["summary"]      
            else:
                summary = await data_summarization(selected_method_label="llm", temperature=0.5, user_details=user_data)

            # Generate new goals
            new_goals = self.lida.goals(summary, n=goals_count.goalCount, textgen_config=self.textgen_config)

            if existing_goals:
                # If the goal count matches, return the existing goals
                if goals_count.goalCount == existing_goals["current_goal_count"]:
                    return existing_goals["goals"]

                # Otherwise, update the existing record with new goals
                users_goals_collection.update_one(
                    {"_id": existing_goals["_id"]},
                    {
                        "$set": {
                            "goals": [{"id": goal.index, "question": goal.question, "visualization": goal.visualization} for goal in new_goals],
                            "current_goal_count": goals_count.goalCount,
                        }
                    }
                )
            else:
                # If no record exists, insert a new document
                users_goals_collection.insert_one({
                    "user_name": username,
                    "file_name": file_name,
                    "current_goal_count": goals_count.goalCount,
                    "summary": summary,
                    "goals": [{"id": goal.index, "question": goal.question, "visualization": goal.visualization} for goal in new_goals],
                })

            return new_goals
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in goal generator: {str(e)}")

    
    async def goal_adder(self, new_goal_description, user_data):

        """
        Adds new goals that are added by the user in the database
        
        Args:
            new_goal_description (str): New goal description
            user_data (dict): User data

        Returns:
            JSONResponse: Goals
        
        Raises:
            HTTPException: Internal server error if an error occurs during goal addition
        """

        logger.info(f"Entered goal adder with new goal description: {new_goal_description} and user data: {user_data}")

        try:

            # Fetch existing goals from the database
            existing_goals = users_goals_collection.find_one({"user_name": user_data['username'], "file_name": user_data['file']})

            if not existing_goals:
                raise HTTPException(status_code=404, detail="No existing goals found for the user and file.")

            # Generate the new goal object
            new_goal = Goal(question=new_goal_description, visualization=new_goal_description, rationale="")

            # Add the new goal to the existing goals list
            updated_goals = existing_goals["goals"] + [{
                "id": len(existing_goals["goals"]) + 1,
                "question": new_goal.question,
                "visualization": new_goal.visualization
            }]

            # Update the database record with the new goals list
            users_goals_collection.update_one(
                {"_id": existing_goals["_id"]},
                {
                    "$set": {
                        "goals": updated_goals,
                        "current_goal_count": len(updated_goals),
                    }
                }
            )

            return updated_goals, updated_goals[-1]
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in goal adder: {str(e)}")
