import pandas as pd
from fastapi import HTTPException
from typing import Optional, List
from sklearn.ensemble import RandomForestClassifier

from feature_engine.selection import (DropFeatures,DropConstantFeatures, 
                                      DropDuplicateFeatures, DropCorrelatedFeatures, 
                                      SmartCorrelatedSelection, SelectByShuffling, 
                                      SelectBySingleFeaturePerformance,RecursiveFeatureElimination)

from Components.Logger import logger
from Components.data import get_edited_dataframe_details, get_user_details, fetch_and_read_github_file



class FeatureSelection:

    """
    Class to handle the feature selection tasks
    """

    def __init__(self, 
                 user_details: dict, 
                 selection_columns: Optional[List[str]] = None,
                 featureselectionSubTask : Optional[str] = None,
                 target_feature: Optional[str] = None
                 ):

        self.user_details = user_details
        self.selection_columns = selection_columns
        self.featureselectionSubTask = featureselectionSubTask
        self.target_feature = target_feature

    async def handle_dataframe(self,
                               user_details: dict
                               ):

        """
        Handle the dataframe based on the user details

        Args:
            user_details (dict): User details including username and role

        Returns:
            pd.DataFrame: The dataframe

        Raises:
            HTTPException: Error in handling dataframe during feature selection
        """

        logger.info(f"Entered in 'handle_dataframe in feature selection' function")

        try:
            user_data = get_user_details(username=user_details['username'], role=user_details['role'])

            users_edited_dataframe_info = get_edited_dataframe_details(user_details['username'], user_details['role'], user_data["file"])

            # If the dataframe is already edited, then read the edited dataframe else read the original dataframe
            if users_edited_dataframe_info:
                dataset = await fetch_and_read_github_file(users_edited_dataframe_info["edited_file"], users_edited_dataframe_info["edited_file_url"])
                need_to_update = False
            else:
                dataset = await fetch_and_read_github_file(user_data["file"], user_data["file_url"])
                need_to_update = True

            return dataset,need_to_update
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in handling dataframe during feature selection: {str(e)}")
        
    def manager(self,
                dataset: pd.DataFrame
                ):
        
        """
        Manager function to handle the feature selection tasks based on the sub task

        Args:
            dataset (pd.DataFrame): The dataframe

        Returns:
            pd.DataFrame: The dataframe

        Raises:
            HTTPException: Error in manager function during feature selection
        """

        logger.info(f"Entered in 'manager in feature selection' function")

        try:

            selection_columns = self.selection_columns
            target_feature = self.target_feature
            sub_task = self.featureselectionSubTask

            if sub_task == "DropFeatures":
                
                edited_dataset = self.drop_features(dataset, selection_columns)
                return edited_dataset
            
            elif sub_task == "DropConstantFeatures":
                
                edited_dataset = self.drop_constant_features(dataset)
                return edited_dataset
            
            elif sub_task == "DropDuplicateFeatures":
                
                edited_dataset = self.drop_duplicate_features(dataset)
                return edited_dataset
            
            elif sub_task == "DropCorrelatedFeatures":
                
                edited_dataset = self.drop_correlated_features(dataset)
                return edited_dataset
            
            elif sub_task == "SmartCorrelationSelection":
                
                edited_dataset = self.smart_correlation_selection(dataset)

                return edited_dataset
            
            elif sub_task == "ShuffleFeaturesSelector":
                
                edited_dataset = self.shuffle_features_selector(dataset, target_feature)
                return edited_dataset
            
            elif sub_task == "SelectBySingleFeaturePerformance":
                
                edited_dataset = self.select_by_single_feature_performance(dataset, target_feature)
                return edited_dataset
            
            elif sub_task == "RecursiveFeatureElimination":
                
                edited_dataset = self.recursive_feature_elimination(dataset, target_feature)
                return edited_dataset
            
            else:
                raise HTTPException(status_code=400, detail="Invalid sub task")
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in manager function during feature selection: {str(e)}")
    
    def drop_features(self,
                      dataset: pd.DataFrame, 
                      selection_columns: List[str]
                      ):
        
        """
        Drop the features from the dataframe
        """

        logger.info(f"Entered in 'drop_features in feature selection' function")

        try:
    
            drop_features = DropFeatures(features_to_drop=selection_columns)
            edited_dataset = drop_features.fit_transform(dataset)
            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in drop features function during feature selection: {str(e)}")
    
    def drop_constant_features(self,
                               dataset: pd.DataFrame
                               ):
        """
        Drop the constant features from the dataframe
        """

        logger.info(f"Entered in 'drop_constant_features in feature selection' function")

        try:

            drop_constant_features = DropConstantFeatures(variables=None)
            edited_dataset = drop_constant_features.fit_transform(dataset)
            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in drop constant features function during feature selection: {str(e)}")
    
    def drop_duplicate_features(self,
                                dataset: pd.DataFrame
                                ):

        """
        Drop the duplicate features from the dataframe
        """

        logger.info(f"Entered in 'drop_duplicate_features in feature selection' function")

        try:

            drop_duplicate_features = DropDuplicateFeatures(variables=None)
            edited_dataset = drop_duplicate_features.fit_transform(dataset)
            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in drop duplicate features function during feature selection: {str(e)}")
    
    def drop_correlated_features(self,
                                 dataset: pd.DataFrame
                                 ):

        """
        Drop the correlated features from the dataframe
        """

        logger.info(f"Entered in 'drop_correlated_features in feature selection' function")

        try:

            drop_correlated_features = DropCorrelatedFeatures(method="pearson", 
                                                              threshold=0.8,
                                                              variables=None
                                                              )
            edited_dataset = drop_correlated_features.fit_transform(dataset)
            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in drop correlated features function during feature selection: {str(e)}")
    
    def smart_correlation_selection(self,
                                    dataset: pd.DataFrame
                                    ):
        
        """
        Smart correlation selection of the features from the dataframe
        """

        logger.info(f"Entered in 'smart_correlation_selection in feature selection' function")

        try:

            smart_correlation_selection = SmartCorrelatedSelection(
                variables=None,
                method="pearson",
                threshold=0.75,
                missing_values="raise",
                selection_method="variance",
                estimator=None,
            )

            edited_dataset = smart_correlation_selection.fit_transform(dataset)

            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in smart correlation selection function during feature selection: {str(e)}")
    
    def shuffle_features_selector(self,
                                  dataset: pd.DataFrame, 
                                  target_feature: str
                                  ):

        """
        Shuffle features selector of the features from the dataframe
        """

        logger.info(f"Entered in 'shuffle_features_selector in feature selection' function")

        try:

            rf = RandomForestClassifier(random_state=42)

            shuffle_features_selector = SelectByShuffling(
                estimator=rf,
                cv=2,
                random_state=42,
            )

            edited_dataset = shuffle_features_selector.fit_transform(dataset,dataset[target_feature])
            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in shuffle features selector function during feature selection: {str(e)}")
    
    def select_by_single_feature_performance(self,
                                             dataset: pd.DataFrame, 
                                             target_feature: str
                                             ):

        """
        Select by single feature performance of the features from the dataframe
        """

        logger.info(f"Entered in 'select_by_single_feature_performance in feature selection' function")

        try:

            rf = RandomForestClassifier(n_estimators=10, 
                                        random_state=1, 
                                        n_jobs=4
                                        )

            select_by_single_feature_performance = SelectBySingleFeaturePerformance(
                variables=None,
                estimator=rf,
                scoring="roc_auc",
                cv=3,
                threshold=0.5
            )

            edited_dataset = select_by_single_feature_performance.fit_transform(dataset,dataset[target_feature])
            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in select by single feature performance function during feature selection: {str(e)}")
    
    def recursive_feature_elimination(self,
                                      dataset: pd.DataFrame, 
                                      target_feature: str
                                      ):

        """
        Recursive feature elimination of the features from the dataframe
        """

        logger.info(f"Entered in 'recursive_feature_elimination in feature selection' function")

        try:
            
            rf = RandomForestClassifier(random_state=2)

            recursive_feature_elimination = RecursiveFeatureElimination(estimator=rf, 
                                                                        cv=2
                                                                        )

            edited_dataset = recursive_feature_elimination.fit_transform(dataset,dataset[target_feature])
            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in recursive feature elimination function during feature selection: {str(e)}")
    

    

    
    



        
    





