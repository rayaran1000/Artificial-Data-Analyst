import io
import base64
from pydantic import BaseModel
import matplotlib.pyplot as plt
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Depends

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

from Components.Logger import logger
from Components.auth import get_current_user
from Components.goal_generator import GoalGeneration
from Components.database import users_visual_code_collection
from Components.visualization_manager import VisualizationManager
from Components.data import get_user_details, fetch_and_read_github_file

router = APIRouter()

class GoalGenerationRequest(BaseModel):
    """
    Pydantic model for goal generation request
    """
    
    goalCount: int

class GoalAdditionRequest(BaseModel):
    """
    Pydantic model for goal addition request
    """

    description: str
    goalCount: int

class VisualizationsGenerationRequest(BaseModel):
    """
    Pydantic model for visualizations generation request
    """

    goal : dict
    visualization_option : str
    visualization_count : int
    visualization_title : str

class VisualizationTitleGenerationRequest(BaseModel):
    """
    Pydantic model for visualization title generation request
    """

    visualization_count : int

class VisualEditRequest(BaseModel):
    """
    Pydantic model for visualization edit request
    """

    nlpInput : str

@router.post("/visualize/goalgenerator")
async def handle_goal_generation(goals_count : GoalGenerationRequest, 
                                 user_details: dict = Depends(get_current_user)
                                 ):
    
    """Handles the generation of goals

    Args:
        goals_count (GoalGenerationRequest): The number of goals to generate
        user_details (dict): The user details

    Returns:
        JSONResponse: The generated goals
    
    Raises:
        HTTPException: If there is an error during goal generation
    """

    logger.info(f"Entered handle_goal_generation with goals_count: {goals_count} and user_details: {user_details}")

    try:

        # Instantiate the goal generator
        goal_generator = GoalGeneration()

        user_data = get_user_details(username=user_details['username'], role=user_details['role'])

        # Generate goals
        goals = await goal_generator.goal_generator(goals_count, user_data)

        # Convert to the required format
        formatted_goals = {
            "goals": [{"id": goal.index, "question": goal.question} for goal in goals]
        }

        return JSONResponse(content=formatted_goals)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during handle goal generation: {str(e)}")
    
@router.post("/visualize/goaladdition")
async def handle_goal_addition(new_goal : GoalAdditionRequest, 
                               user_details: dict = Depends(get_current_user)
                               ):
    
    """Handles the addition of goals

    Args:
        new_goal (GoalAdditionRequest): The new goal to add
        user_details (dict): The user details

    Returns:
        JSONResponse: The added goal
    
    Raises:
        HTTPException: If there is an error during goal addition
    """

    logger.info(f"Entered handle_goal_addition with new_goal: {new_goal} and user_details: {user_details}")

    try:

        # Instantiate the goal generator
        goal_generator = GoalGeneration()

        user_data = get_user_details(username=user_details['username'], role=user_details['role'])

        # Add the new goal
        updated_goals, added_goal = await goal_generator.goal_adder(
            new_goal_description=new_goal.description,
            goals_count=new_goal.goalCount,
            user_data=user_data
        )

        formatted_new_goal = {
            "id": added_goal["id"],
            "question": added_goal["question"]
        }
        
        return JSONResponse(content=formatted_new_goal)
    
    except HTTPException as http_exc:
        raise http_exc
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during handle goal addition: {str(e)}")

@router.post("/visualize/visualization-titles")
async def handle_visualization_title_generation(visualization_title_request : VisualizationTitleGenerationRequest, 
                                                user_details: dict = Depends(get_current_user)
                                                ):
    
    """Handles the title generation for visuals created

    Args:
        visualization_title_request (VisualizationTitleGenerationRequest): The number of visualization titles to generate
        user_details (dict): The user details

    Returns:
        JSONResponse: The generated visualization titles
    
    Raises:
        HTTPException: If there is an error during visualization title generation
    """

    logger.info(f"Entered handle_visualization_title_generation with visualization_title_request: {visualization_title_request} and user_details: {user_details}")

    try:
        # Instantiate the visualization generator
        visualization_manager = VisualizationManager()

        visualization_titles = await visualization_manager.visual_title_generator(visualization_title_request.visualization_count)

        return JSONResponse({"visualizationTitles" : visualization_titles})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during handle visualization title generation: {str(e)}")

@router.post("/visualize/clear-db")
async def handle_visual_database_clearing():
    
    """Handles the clearing of the visual database

    Raises:
        HTTPException: If there is an error during visualization database clearing
    """
    
    try:

        visualization_manager = VisualizationManager()

        await visualization_manager.clear_code_database()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during visual database clearing: {str(e)}")

@router.post("/visualize/visualizations")
async def handle_visualizations_generation(visualization_request: VisualizationsGenerationRequest, 
                                           user_details: dict = Depends(get_current_user)
                                           ):
    
    """Handles the generation of visualizations

    Args:
        visualization_request (VisualizationsGenerationRequest): The visualization request
        user_details (dict): The user details

    Returns:
        JSONResponse: The generated visualization
    
    Raises:
        HTTPException: If there is an error during visualization generation
    """

    logger.info(f"Entered handle_visualizations_generation with visualization_request: {visualization_request} and user_details: {user_details}")

    try:

        visualization_manager = VisualizationManager()
        user_data = get_user_details(username=user_details['username'], role=user_details['role'])
        dataset = await fetch_and_read_github_file(user_data["file"], user_data["file_url"])

        # Clear any existing plots
        plt.clf()

        # Get the visualization
        selected_viz = await visualization_manager.visual_generator(
            visualization_request.goal,
            visualization_request.visualization_option,
            visualization_request.visualization_count,
            visualization_request.visualization_title,
            user_data,
            dataset
        )

        # Create a new figure with specific size
        plt.figure(figsize=(10, 6))
        
        # If it's a list, take the first visualization
        if isinstance(selected_viz, list):
            viz_data = selected_viz[0]
        else:
            viz_data = selected_viz

        # If the visualization is already a base64 string
        if hasattr(viz_data, 'raster') and viz_data.raster:
            # Clean the base64 string - remove any newlines or extra text
            base64_string = viz_data.raster.split(',')[-1].strip()
        else:
            # Ensure clean plot
            plt.tight_layout(pad=0.1)
            plt.axis('off')
            
            # Save to bytes with clean parameters
            img_byte_arr = io.BytesIO()
            plt.savefig(img_byte_arr, 
                       format='png',
                       bbox_inches='tight',
                       pad_inches=0,
                       transparent=True,
                       dpi=300)
            img_byte_arr.seek(0)
            base64_string = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            
            # Close the figure
            plt.close('all')

        # Return clean JSON response
        return {
            "visualization": {
                "raster": base64_string,
                "type": "image/png"
            }
        }

    except Exception as e:
        plt.close('all')  # Ensure all plots are closed even on error
        raise HTTPException(status_code=500, detail=f"Error during handle visualizations generation: {str(e)}")

@router.post("/visualize/edit-visualization")
async def handle_visual_editing(instruction : VisualEditRequest, 
                                user_details: dict = Depends(get_current_user)
                                ):
    
    """Handles the editing of visualizations

    Args:
        instruction (VisualEditRequest): The instruction to edit the visualization
        user_details (dict): The user details

    Returns:
        JSONResponse: The edited visualization
    
    Raises:
        HTTPException: If there is an error during visualization editing
    """

    logger.info(f"Entered handle_visual_editing with instruction: {instruction} and user_details: {user_details}")

    try:

        user_data = get_user_details(username=user_details['username'], role=user_details['role'])       

        # Fetch the visualization details from the database

        visualization_data = users_visual_code_collection.find_one({"username" : user_data['username'] , "file_name" : user_data['file']}) 

        # Fetching dataset
        user_data = get_user_details(username=user_details['username'], role=user_details['role'])
        dataset = await fetch_and_read_github_file(user_data["file"], user_data["file_url"])

        # Instantiate the visualization generator
        visualization_manager = VisualizationManager()

        edited_visualization = await visualization_manager.visual_editor(instruction.nlpInput,visualization_data,dataset)

        # Clear any existing plots
        plt.clf()

        # Create a new figure with specific size
        plt.figure(figsize=(10, 6))
        
        # If it's a list, take the first visualization
        if isinstance(edited_visualization, list):
            viz_data = edited_visualization[0]
        else:
            viz_data = edited_visualization

        # If the visualization is already a base64 string
        if hasattr(viz_data, 'raster') and viz_data.raster:
            # Clean the base64 string - remove any newlines or extra text
            base64_string = viz_data.raster.split(',')[-1].strip()
        else:
            # Ensure clean plot
            plt.tight_layout(pad=0.1)
            plt.axis('off')
            
            # Save to bytes with clean parameters
            img_byte_arr = io.BytesIO()
            plt.savefig(img_byte_arr, 
                       format='png',
                       bbox_inches='tight',
                       pad_inches=0,
                       transparent=True,
                       dpi=300)
            img_byte_arr.seek(0)
            base64_string = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            
            # Close the figure
            plt.close('all')

        # Return clean JSON response
        return {
            "visualization": {
                "raster": base64_string,
                "type": "image/png"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during handle visual editing: {str(e)}")
       
@router.get('/visualize/undo-edit')
async def undo_editing(user_details: dict = Depends(get_current_user)):
    
    """Handles the undoing of edits

    Args:
        user_details (dict): The user details

    Returns:
        JSONResponse: The last edited visualization
    
    Raises:
        HTTPException: If there is an error during visualization undo editing
    """

    logger.info(f"Entered handle_undo_editing with user_details: {user_details}")
    
    try:

        visualization_manager = VisualizationManager()
        user_data = get_user_details(username=user_details['username'], role=user_details['role'])

        # Fetch data from database
        dataset = await fetch_and_read_github_file(user_data["file"], user_data["file_url"])
        
        last_edited_visual = await visualization_manager.visual_edit_undoer(user_data, dataset)

        # Clear any existing plots
        plt.clf()

        # Create a new figure with specific size
        plt.figure(figsize=(10, 6))
        
        # If it's a list, take the first visualization
        if isinstance(last_edited_visual, list):
            viz_data = last_edited_visual[0]
        else:
            viz_data = last_edited_visual

        # If the visualization is already a base64 string
        if hasattr(viz_data, 'raster') and viz_data.raster:
            # Clean the base64 string - remove any newlines or extra text
            base64_string = viz_data.raster.split(',')[-1].strip()
        else:
            # Ensure clean plot
            plt.tight_layout(pad=0.1)
            plt.axis('off')
            
            # Save to bytes with clean parameters
            img_byte_arr = io.BytesIO()
            plt.savefig(img_byte_arr, 
                       format='png',
                       bbox_inches='tight',
                       pad_inches=0,
                       transparent=True,
                       dpi=300)
            img_byte_arr.seek(0)
            base64_string = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            
            # Close the figure
            plt.close('all')

        # Return clean JSON response
        return {
            "visualization": {
                "raster": base64_string,
                "type": "image/png"
            }
        }


    except Exception as e:
        plt.close('all')  # Ensure all plots are closed even on error
        raise HTTPException(status_code=500, detail=f"Error during handle undo editing: {str(e)}")   
    

@router.get('/visualize/explain-visualization')
async def handle_visual_explanation(user_details: dict = Depends(get_current_user)):
    
    """Handles the explanation of visualizations

    Args:
        user_details (dict): The user details

    Returns:
        JSONResponse: The explanation of the visualization
    
    Raises:
        HTTPException: If there is an error during visualization explanation
    """

    logger.info(f"Entered handle_visual_explanation with user_details: {user_details}")

    try:

        visualization_manager = VisualizationManager()
        user_data = get_user_details(username=user_details['username'], role=user_details['role'])

        explanation = await visualization_manager.visual_explainer(user_data)

        return explanation[0][0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during handle visual explanation: {str(e)}") 
    

# Visualization Evaluator
@router.get('/visualize/evaluate-visualization')
async def handle_visual_evaluation(user_details : dict = Depends(get_current_user)):
    
    """Handles the evaluation of visualizations

    Args:
        user_details (dict): The user details

    Returns:
        JSONResponse: The evaluation of the visualization

    Raises:
        HTTPException: If there is an error during visualization evaluation
    """

    logger.info(f"Entered handle_visual_evaluation with user_details: {user_details}")

    try:

        user_data = get_user_details(username=user_details['username'], role=user_details['role'])

        visualization_manager = VisualizationManager()
        
        evaluations = await visualization_manager.visual_evaluator(user_data)

        # Process evaluations for better readability
        formatted_evaluations = [
            {
                "dimension": f"{eval['dimension']}",
                "score": f"Score: {eval['score']} / 10",
                "rationale": eval["rationale"],
                "separator": "**********************************"
            }
            for eval in evaluations[0]  # Assuming evaluations[0] contains the list
        ]

        return JSONResponse(content={"evaluation": formatted_evaluations}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during handle visual evaluation: {str(e)}")