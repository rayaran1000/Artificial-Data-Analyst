from fastapi import HTTPException

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
from Components.database import users_goals_collection, users_visual_code_collection


class VisualizationManager:

    """
    Handles visualization related functionalities
    """

    editing_stage = 0 # Variable that indicates the number of edits done

    def __init__(self):

        self.model_name = "llama3-70b-8192"
        self.text_gen = llm(provider="chatgroq", model=self.model_name)
        self.lida = Manager(text_gen=self.text_gen)

    async def visual_generator(self,selected_goal,visualization_option,num_visualizations,visualization_title,user_data, dataset):

        """
        Generates Visualizations as per user request and goals
        
        Args:
            selected_goal (dict): Selected goal
            visualization_option (str): Visualization option
            num_visualizations (int): Number of visualizations
            visualization_title (str): Visualization title
            user_data (dict): User data
            dataset (pd.DataFrame): Dataset
        
        Returns:
            list: Visualizations
        
        Raises:
            HTTPException: Internal server error if an error occurs during visualization generation
        """

        logger.info(f"Entered visual generator with selected goal: {selected_goal}, visualization option: {visualization_option}, number of visualizations: {num_visualizations}, visualization title: {visualization_title}, user data: {user_data}, dataset: {dataset}")

        try:

            textgen_config = TextGenerationConfig(n=num_visualizations,temperature=0.5,use_cache=True,model=self.model_name)

            # Fetch summary information
            summary_details = users_goals_collection.find_one({"user_name": user_data['username'], "file_name": user_data['file']})

            summary = summary_details["summary"]

            selected_goal_object = next((x for x in summary_details["goals"] if x["question"] == selected_goal['question']), None)

            selected_goal_object["rationale"] = ""

            visualization = self.lida.visualize(summary=summary,goal=selected_goal_object,textgen_config=textgen_config,library=visualization_option,dataframe=dataset)

            VisualizationManager.editing_stage = 0

            # Searching for Existing code for editing (Undo button)
            existing_code_record = users_visual_code_collection.find_one(
                {"username": user_data['username'], "file_name": user_data['file'], "goal.visualization": selected_goal_object['visualization'], "visualization_title" : visualization_title, "library" : visualization_option}
            )

            if existing_code_record:
                users_visual_code_collection.update_one(
                    {"_id": existing_code_record["_id"]},
                    {
                        "$push": {"code": [visualization[0].code]},
                        "$inc": {"total_edits" : 1}
                    }
                )
            else:
                users_visual_code_collection.insert_one({
                    "username": user_data['username'],
                    "file_name": user_data['file'],
                    "goal": selected_goal_object,
                    "visualization_title": visualization_title,
                    "summary": summary,
                    "library": visualization_option,
                    "code": [visualization[0].code],
                    "total_edits": 1
                })

            return visualization
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in visual generator: {str(e)}")
    
    
    async def visual_title_generator(self,visualization_count):
        
        """
        Generates titles for all visualizations
        
        Args:
            visualization_count (int): Number of visualizations

        Returns:
            list: Visualization titles

        Raises:
            HTTPException: Internal server error if an error occurs during visualization title generation
        """

        try:

            visualization_titles = [f'Visualization {i+1}' for i in range(visualization_count)]

            return visualization_titles
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in visual title generator: {str(e)}")
    
    async def clear_code_database(self):
        
        """
        Clears the code database when edit is completed

        Raises:
            HTTPException: Internal server error if an error occurs during code database clearing
        """

        try:

            # Clear the code database
            users_visual_code_collection.delete_many({})
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in clear code database: {str(e)}")

    
    async def visual_edit_undoer(self, user_data, dataset):
        
        """
        Undo button functionality to reverse the edit done

        Args:
            user_data (dict): User data
            dataset (pd.DataFrame): Dataset

        Returns:
            list: Visualizations    

        Raises:
            HTTPException: Internal server error if an error occurs during visualization edit undo
        """

        logger.info(f"Entered visual edit undoer with user data: {user_data} and dataset: {dataset}")

        try:
            # Fetch existing code first
            existing_code_record = users_visual_code_collection.find_one(
                {"username": user_data['username'], "file_name": user_data['file']}
            )

            if not existing_code_record:
                raise HTTPException(status_code=404, detail="No visualization history found")

            if existing_code_record["total_edits"] <= 1:
                raise HTTPException(status_code=400, detail="No previous edits to undo")

            # Update the record
            users_visual_code_collection.update_one(
                {"_id": existing_code_record["_id"]},
                {
                    "$pop": {"code": 1},
                    "$inc": {"total_edits": -1}
                }
            )

            VisualizationManager.editing_stage -= 1

            # Fetch the updated record
            existing_code_record_updated = users_visual_code_collection.find_one(
                {"_id": existing_code_record["_id"]}
            )
            
            if not existing_code_record_updated or not existing_code_record_updated["code"]:
                raise HTTPException(status_code=404, detail="No visualization code found after undo")

            # Execute the previous version
            last_edited_visual = self.lida.execute(
                code_specs=[existing_code_record_updated["code"][-1]], 
                data=dataset, 
                summary=existing_code_record_updated["summary"],
                library=existing_code_record_updated["library"]
            )
            
            return last_edited_visual

        except HTTPException as he:
            # Re-raise HTTP exceptions
            raise he
        except Exception as e:
            logger.error(f"Error in visual edit undoer: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error in visual edit undoer: {str(e)}")
    
    async def visual_editor(self, instruction, visualization_data, dataset):
        
        """
        Visual Editor using Natural Language
        
        Args:
            instruction (str): Instruction
            visualization_data (dict): Visualization data
            dataset (pd.DataFrame): Dataset

        Returns:
            list: Visualizations

        Raises:
            HTTPException: Internal server error if an error occurs during visualization editing
        """

        logger.info(f"Entered visual editor with instruction: {instruction}, visualization data: {visualization_data}, dataset: {dataset}")

        try:            
            
            textgen_config = TextGenerationConfig(n=1,temperature=0,use_cache=True,model=self.model_name)

            edited_visualization = self.lida.edit(code=visualization_data["code"][VisualizationManager.editing_stage] , summary=visualization_data["summary"], instructions=[instruction], textgen_config=textgen_config, library=visualization_data["library"],data=dataset)

            # Add the new edited code in the database
            users_visual_code_collection.update_one(
                    {"_id": visualization_data["_id"]},
                    {
                        "$push": {"code": edited_visualization[0].code},
                        "$inc": {"total_edits" : 1}
                    }
                )

            VisualizationManager.editing_stage += 1

            return edited_visualization
    
        except Exception as e:
                logger.error(f"Error in visual editor: {str(e)}")
                raise HTTPException(status_code=500, detail="Internal Server Error")
        
    async def visual_explainer(self,user_data):
        
        """Explains the visual information"""

        try:

            textgen_config = TextGenerationConfig(n=1,temperature=0,use_cache=True,model=self.model_name)

            # Fetch existing code
            existing_code_record = users_visual_code_collection.find_one(
                {"username": user_data['username'], "file_name": user_data['file']}
            )

            explanation = self.lida.explain(code=existing_code_record["code"][-1],textgen_config=textgen_config,library=existing_code_record["library"])

            return explanation

        except Exception as e:
            logger.error(f"Error in visual explainer: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    async def visual_evaluator(self,user_data):
        
        """
        Evaluates the visual code and returns suggestions
        
        Args:
            user_data (dict): User data

        Returns:
            list: Evaluations

        Raises:
            HTTPException: Internal server error if an error occurs during visualization evaluation
        """

        logger.info(f"Entered visual evaluator with user data: {user_data}")

        try:
            
            textgen_config = TextGenerationConfig(n=1,temperature=0,use_cache=True,model=self.model_name)

            # Fetch existing code
            existing_code_record = users_visual_code_collection.find_one(
                {"username": user_data['username'], "file_name": user_data['file']}
            )

            goal = Goal(question=existing_code_record["goal"]["question"], visualization=existing_code_record["goal"]["visualization"], rationale=existing_code_record["goal"]["rationale"])

            evaluations = self.lida.evaluate(code=existing_code_record["code"][-1],goal=goal,textgen_config=textgen_config,library=existing_code_record["library"])

            return evaluations            

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during visual evaluator: {str(e)}")
