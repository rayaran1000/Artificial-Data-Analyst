import pandas as pd
from fastapi import HTTPException
from typing import Optional, List
from sklearn.model_selection import train_test_split

from feature_engine.imputation import (MeanMedianImputer,RandomSampleImputer, 
                                       EndTailImputer, CategoricalImputer)

from feature_engine.encoding import (OneHotEncoder, OrdinalEncoder, 
                                     CountFrequencyEncoder, MeanEncoder)

from feature_engine.discretisation import (EqualFrequencyDiscretiser, EqualWidthDiscretiser, 
                                           GeometricWidthDiscretiser, DecisionTreeDiscretiser)

from feature_engine.outliers import Winsorizer
from feature_engine.transformation import (LogTransformer, LogCpTransformer,
                                            ReciprocalTransformer, PowerTransformer, 
                                            BoxCoxTransformer, YeoJohnsonTransformer)

from feature_engine.scaling import MeanNormalizationScaler
from feature_engine.datetime import DatetimeFeatures

from Components.Logger import logger
from Components.data import get_edited_dataframe_details, get_user_details, fetch_and_read_github_file

class FeatureEngineering:

    """
    Class to handle the feature engineering tasks
    """

    def __init__(self, 
                 user_details: dict, 
                 engineering_columns: Optional[List[str]] = None, 
                 target_feature: Optional[str] = None,
                 featureengineeringTask : Optional[str] = None, 
                 featureengineeringSubTask : Optional[str] = None
                 ):

        self.user_details = user_details
        self.engineering_columns = engineering_columns
        self.target_feature = target_feature
        self.featureengineeringTask = featureengineeringTask
        self.featureengineeringSubTask = featureengineeringSubTask
    
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
            HTTPException: Error in handling dataframe during feature engineering
        """

        logger.info(f"Entered in 'handle_dataframe in feature engineering' function")

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
            raise HTTPException(status_code=500, detail=f"Error in handling dataframe during feature engineering: {str(e)}")
    
    def train_test_split(self,
                         dataset: pd.DataFrame, 
                         independent_features: List[str], 
                         target_feature: str
                         ):

        """
        Handle the training and testing of the dataset

        Args:
            dataset (pd.DataFrame): The dataframe
            independent_features (List[str]): The independent features
            target_feature (str): The target feature

        Returns:
            pd.DataFrame: The training set  
            pd.DataFrame: The testing set
            pd.DataFrame: The training target
            pd.DataFrame: The testing target

        Raises:
            HTTPException: Error in splitting the dataset into training and testing sets
        """

        logger.info(f"Entered in 'train_test_split' function")

        try:

            X = dataset[independent_features]
            y = dataset[target_feature]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

            return X_train, X_test, y_train, y_test
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in splitting the dataset into training and testing sets: {str(e)}")
    

    def manager(self,dataset: pd.DataFrame):

        """
        Manager function to handle the feature engineering tasks based on the task and sub task

        Args:
            dataset (pd.DataFrame): The dataframe

        Returns:
            pd.DataFrame: The edited dataframe

        Raises:
            HTTPException: Error in manager function during feature engineering
        """

        logger.info(f"Entered in 'manager' function")

        try:

            independent_features = self.engineering_columns
            target_feature = self.target_feature
            task = self.featureengineeringTask
            sub_task = self.featureengineeringSubTask

            X_train, X_test, y_train, y_test = self.train_test_split(dataset, independent_features, target_feature)

            if task == "Missing Data Imputation":

                if sub_task == "MedianImputer":
                    
                    edited_dataset = self.median_imputer(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "MeanImputer":

                    edited_dataset = self.mean_imputer(X_train, X_test, dataset, independent_features)
                    return edited_dataset

                elif sub_task == "RandomSampleImputer":
                    
                    edited_dataset = self.random_sample_imputer(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "EndTailImputer":

                    edited_dataset = self.end_tail_imputer(X_train, X_test, dataset, independent_features)

                    return edited_dataset
                
                elif sub_task == "AddMissingIndicator":

                    edited_dataset = self.categorical_imputer(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "DropMissingData":
                    
                    edited_dataset = self.drop_missing_data(dataset, independent_features)
                    return edited_dataset
            
            elif task == "Categorical Encoding":
                
                if sub_task == "OneHotEncoder":
                    
                    edited_dataset = self.one_hot_encoder(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "OrdinalEncoder":
                    
                    edited_dataset = self.ordinal_encoder(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "CountEncoder":
                    
                    edited_dataset = self.count_encoder(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "FrequencyEncoder":
                    
                    edited_dataset = self.frequency_encoder(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "MeanEncoder":
                    
                    edited_dataset = self.mean_encoder(X_train, X_test, y_train, dataset, independent_features)
                    return edited_dataset
            
            elif task == "Discretisation":

                if sub_task == "EqualFrequencyDiscretiser":
                    
                    edited_dataset = self.equal_frequency_discretiser(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "EqualWidthDiscretiser":
                    
                    edited_dataset = self.equal_width_discretiser(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "GeometricWidthDiscretiser":
                    
                    edited_dataset = self.geometric_width_discretiser(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "DecisionTreeDiscretiser":
                    
                    edited_dataset = self.decision_tree_discretiser(X_train, X_test, y_train, dataset, independent_features)
                    return edited_dataset

            
            elif task == "Outlier Capping or Removal":

                if sub_task == "GaussianOutlierCapper":
                    
                    edited_dataset = self.gaussian_outlier_capping(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "IQROutlierCapper":
                    
                    edited_dataset = self.iqr_outlier_capping(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
            elif task == "Feature Transformation":

                if sub_task == "LogTransformer":
                    
                    edited_dataset = self.log_transformer(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "LogCpTransformer":
                    
                    edited_dataset = self.log_cp_transformer(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "ReciprocalTransformer":

                    edited_dataset = self.reciprocal_transformer(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "SquareRootTransformer":
                    
                    edited_dataset = self.square_root_transformer(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "BoxCoxTransformer":
                    
                    edited_dataset = self.box_cox_transformer(X_train, X_test, dataset, independent_features)
                    return edited_dataset
                
                elif sub_task == "YeoJohnsonTransformer":
                    
                    edited_dataset = self.yeo_johnson_transformer(X_train, X_test, dataset, independent_features)
                    return edited_dataset
            
            elif task == "Feature Scaling":

                if sub_task == "MeanNormalizationScaler":
                    
                    edited_dataset = self.mean_normalization_scaler(X_train, X_test, dataset, independent_features)
                    return edited_dataset
            
            elif task == "Datetime Feature Handling":

                if sub_task == "DatetimeFeatures":
                    
                    edited_dataset = self.datetime_features(dataset)
                    return edited_dataset
            else:
                raise HTTPException(status_code=400, detail="Invalid task or sub task")
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in manager function during feature engineering: {str(e)}")
    
    def median_imputer(self, 
                       X_train: pd.DataFrame, 
                       X_test: pd.DataFrame, 
                       dataset: pd.DataFrame, 
                       independent_features: List[str]
                       ):

        """
        Handle the median imputation of the dataset
        """
        logger.info(f"Entered in 'median_imputer' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()
            
            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            imputer = MeanMedianImputer(imputation_method="median", 
                                        variables=independent_features
                                        )

            X_train = imputer.fit_transform(X_train)
            X_test = imputer.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)
            
            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in median_imputer function during feature engineering: {str(e)}")
    
    def mean_imputer(self, 
                     X_train: pd.DataFrame, 
                     X_test: pd.DataFrame, 
                     dataset: pd.DataFrame, 
                     independent_features: List[str]
                     ):

        """
        Handle the mean imputation of the dataset
        """

        logger.info(f"Entered in 'mean_imputer' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()
            
            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            imputer = MeanMedianImputer(imputation_method="mean", 
                                        variables=independent_features
                                        )

            X_train = imputer.fit_transform(X_train)
            X_test = imputer.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)
            
            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in mean_imputer function during feature engineering: {str(e)}")

    def random_sample_imputer(self, 
                              X_train: pd.DataFrame, 
                              X_test: pd.DataFrame, 
                              dataset: pd.DataFrame, 
                              independent_features: List[str]
                              ):
        
        """
        Handle the random sample imputation of the dataset
        """

        logger.info(f"Entered in 'random_sample_imputer' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()
            
            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            imputer = RandomSampleImputer(variables=independent_features,
                                          random_state=10,
                                          seed="general"
                                          )

            X_train = imputer.fit_transform(X_train)
            X_test = imputer.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)
            
            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in random_sample_imputer function during feature engineering: {str(e)}")
    
    def end_tail_imputer(self, 
                         X_train: pd.DataFrame, 
                         X_test: pd.DataFrame, 
                         dataset: pd.DataFrame, 
                         independent_features: List[str]
                         ):

        """
        Handle the end tail imputation of the dataset
        """

        logger.info(f"Entered in 'end_tail_imputer' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()
            
            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            imputer = EndTailImputer(variables=independent_features,
                                     fold=3,tail="right",
                                     imputation_method="gaussian")

            X_train = imputer.fit_transform(X_train)
            X_test = imputer.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)
            
            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in end_tail_imputer function during feature engineering: {str(e)}")
    
    def categorical_imputer(self, 
                            X_train: pd.DataFrame, 
                            X_test: pd.DataFrame, 
                            dataset: pd.DataFrame, 
                            independent_features: List[str]
                            ):

        """
        Handle the categorical imputation of the dataset
        """

        logger.info(f"Entered in 'categorical_imputer' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()
            
            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            imputer = CategoricalImputer(variables=independent_features,
                                         imputation_method="missing"
                                         )

            X_train = imputer.fit_transform(X_train)
            X_test = imputer.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)
            
            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in categorical_imputer function during feature engineering: {str(e)}")
    
    def drop_missing_data(self, 
                          dataset: pd.DataFrame, 
                          independent_features: List[str]
                          ):

        """
        Handle the dropping of missing data from the dataset
        """

        logger.info(f"Entered in 'drop_missing_data' function")

        try:

            edited_dataset = dataset.dropna(subset=independent_features)

            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in drop_missing_data function during feature engineering: {str(e)}")

    def one_hot_encoder(self, 
                        X_train: pd.DataFrame, 
                        X_test: pd.DataFrame, 
                        dataset: pd.DataFrame, 
                        independent_features: List[str]
                        ):
        
        """
        Handle the one hot encoding of the dataset
        """

        logger.info(f"Entered in 'one_hot_encoder' function")

        try:

            # Store original index
            original_index = dataset.index

            # Convert the independent features to object type
            X_train[independent_features] = X_train[independent_features].astype(object)
            X_test[independent_features] = X_test[independent_features].astype(object)

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            encoder = OneHotEncoder(variables=independent_features,
                                    top_categories=None,
                                    drop_last=False
                                    )

            X_train = encoder.fit_transform(X_train)
            X_test = encoder.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in one_hot_encoder function during feature engineering: {str(e)}")
    
    def ordinal_encoder(self, 
                        X_train: pd.DataFrame, 
                        X_test: pd.DataFrame, 
                        dataset: pd.DataFrame, 
                        independent_features: List[str]
                        ):
        
        """
        Handle the ordinal encoding of the dataset
        """

        logger.info(f"Entered in 'ordinal_encoder' function")

        try:

            # Store original index
            original_index = dataset.index

            # Convert the independent features to object type
            X_train[independent_features] = X_train[independent_features].astype(object)
            X_test[independent_features] = X_test[independent_features].astype(object)

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            encoder = OrdinalEncoder(variables=independent_features,
                                     encoding_method="arbitrary"
                                     )

            X_train = encoder.fit_transform(X_train)
            X_test = encoder.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in ordinal_encoder function during feature engineering: {str(e)}")
    
    def count_encoder(self, 
                       X_train: pd.DataFrame, 
                       X_test: pd.DataFrame, 
                       dataset: pd.DataFrame, 
                       independent_features: List[str]
                       ):
        
        """
        Handle the count encoding of the dataset
        """

        logger.info(f"Entered in 'count_encoder' function")

        try:

            # Store original index
            original_index = dataset.index

            # Convert the independent features to object type
            X_train[independent_features] = X_train[independent_features].astype(object)
            X_test[independent_features] = X_test[independent_features].astype(object)

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            encoder = CountFrequencyEncoder(variables=independent_features,
                                            encoding_method="count"
                                            )

            X_train = encoder.fit_transform(X_train)
            X_test = encoder.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in count_encoder function during feature engineering: {str(e)}")
    
    def frequency_encoder(self, 
                          X_train: pd.DataFrame, 
                          X_test: pd.DataFrame, 
                          dataset: pd.DataFrame, 
                          independent_features: List[str]
                          ):
        
        """
        Handle the frequency encoding of the dataset
        """

        logger.info(f"Entered in 'frequency_encoder' function")

        try:

            # Store original index
            original_index = dataset.index

            # Convert the independent features to object type
            X_train[independent_features] = X_train[independent_features].astype(object)
            X_test[independent_features] = X_test[independent_features].astype(object)

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            encoder = CountFrequencyEncoder(variables=independent_features,
                                            encoding_method="frequency"
                                            )

            X_train = encoder.fit_transform(X_train)
            X_test = encoder.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in frequency_encoder function during feature engineering: {str(e)}")
    
    def mean_encoder(self, 
                     X_train: pd.DataFrame, 
                     X_test: pd.DataFrame, 
                     y_train: pd.DataFrame, 
                     dataset: pd.DataFrame, 
                     independent_features: List[str]
                     ):
        
        """
        Handle the mean encoding of the dataset
        """

        logger.info(f"Entered in 'mean_encoder' function")

        try:

            # Store original index
            original_index = dataset.index

            # Convert the independent features to object type
            X_train[independent_features] = X_train[independent_features].astype(object)
            X_test[independent_features] = X_test[independent_features].astype(object)

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            encoder = MeanEncoder(variables=independent_features)

            encoder.fit(X_train,y_train)
            X_train = encoder.transform(X_train)
            X_test = encoder.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in mean_encoder function during feature engineering: {str(e)}")
    
    def equal_frequency_discretiser(self, 
                                     X_train: pd.DataFrame, 
                                     X_test: pd.DataFrame, 
                                     dataset: pd.DataFrame, 
                                     independent_features: List[str]
                                     ):
        
        """
        Handle the equal frequency discretisation of the dataset
        """

        logger.info(f"Entered in 'equal_frequency_discretiser' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            discretiser =   EqualFrequencyDiscretiser(variables=independent_features, 
                                                      q=10
                                                      )

            X_train = discretiser.fit_transform(X_train)
            X_test = discretiser.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:  
            raise HTTPException(status_code=500, detail=f"Error in equal_frequency_discretiser function during feature engineering: {str(e)}")
    
    def equal_width_discretiser(self, 
                                 X_train: pd.DataFrame, 
                                 X_test: pd.DataFrame, 
                                 dataset: pd.DataFrame, 
                                 independent_features: List[str]
                                 ):
        
        """
        Handle the equal width discretisation of the dataset
        """

        logger.info(f"Entered in 'equal_width_discretiser' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            discretiser =   EqualWidthDiscretiser(variables=independent_features, 
                                                  bins=10
                                                  )

            X_train = discretiser.fit_transform(X_train)
            X_test = discretiser.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in equal_width_discretiser function during feature engineering: {str(e)}")

    def geometric_width_discretiser(self, 
                                     X_train: pd.DataFrame, 
                                     X_test: pd.DataFrame, 
                                     dataset: pd.DataFrame, 
                                     independent_features: List[str]
                                     ):

        """
        Handle the geometric width discretisation of the dataset
        """

        logger.info(f"Entered in 'geometric_width_discretiser' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            discretiser =   GeometricWidthDiscretiser(variables=independent_features, 
                                                      bins=10
                                                      )

            X_train = discretiser.fit_transform(X_train)
            X_test = discretiser.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:  
            raise HTTPException(status_code=500, detail=f"Error in geometric_width_discretiser function during feature engineering: {str(e)}")

    def decision_tree_discretiser(self, 
                                   X_train: pd.DataFrame, 
                                   X_test: pd.DataFrame, 
                                   y_train: pd.DataFrame, 
                                   dataset: pd.DataFrame, 
                                   independent_features: List[str]
                                   ):
        
        """
        Handle the decision tree discretisation of the dataset
        """

        logger.info(f"Entered in 'decision_tree_discretiser' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            discretiser =   DecisionTreeDiscretiser(variables=independent_features, 
                                                    cv=3, 
                                                    scoring='neg_mean_squared_error',
                                                    regression=True, 
                                                    random_state=29
                                                    )

            discretiser.fit(X_train,y_train)
            X_train = discretiser.transform(X_train)
            X_test = discretiser.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:  
            raise HTTPException(status_code=500, detail=f"Error in decision_tree_discretiser function during feature engineering: {str(e)}")
    
    def gaussian_outlier_capping(self, 
                                  X_train: pd.DataFrame, 
                                  X_test: pd.DataFrame, 
                                  dataset: pd.DataFrame, 
                                  independent_features: List[str]
                                  ):
        
        """
        Handle the gaussian outlier capping of the dataset
        """

        logger.info(f"Entered in 'gaussian_outlier_capping' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            outlier_capper = Winsorizer(variables=independent_features, 
                                        capping_method='gaussian', 
                                        tail='both', 
                                        fold=3
                                        )

            X_train = outlier_capper.fit_transform(X_train)
            X_test = outlier_capper.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:  
            raise HTTPException(status_code=500, detail=f"Error in gaussian_outlier_capping function during feature engineering: {str(e)}")
        
    def iqr_outlier_capping(self, 
                            X_train: pd.DataFrame, 
                            X_test: pd.DataFrame, 
                            dataset: pd.DataFrame, 
                            independent_features: List[str]
                            ):
        
        """
        Handle the iqr outlier capping of the dataset
        """

        logger.info(f"Entered in 'iqr_outlier_capping' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            outlier_capper =   Winsorizer(variables=independent_features, 
                                          capping_method='iqr', 
                                          tail='both'
                                          )

            X_train = outlier_capper.fit_transform(X_train)
            X_test = outlier_capper.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:  
            raise HTTPException(status_code=500, detail=f"Error in iqr_outlier_capping function during feature engineering: {str(e)}")
    
    def log_transformer(self, 
                        X_train: pd.DataFrame, 
                        X_test: pd.DataFrame, 
                        dataset: pd.DataFrame, 
                        independent_features: List[str]
                        ):

        """
        Handle the log transformation of the dataset
        """

        logger.info(f"Entered in 'log_transformer' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            log_transformer =  LogTransformer(variables=independent_features,
                                              base='e'
                                              )

            X_train = log_transformer.fit_transform(X_train)
            X_test = log_transformer.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:  
            raise HTTPException(status_code=500, detail=f"Error in log_transformer function during feature engineering: {str(e)}")
    
    def log_cp_transformer(self, 
                           X_train: pd.DataFrame, 
                           X_test: pd.DataFrame, 
                           dataset: pd.DataFrame, 
                           independent_features: List[str]
                           ):
        
        """
        Handle the log cp transformation of the dataset
        """

        logger.info(f"Entered in 'log_cp_transformer' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            log_cp_transformer =  LogCpTransformer(variables=independent_features, 
                                                   C='auto'
                                                   )

            X_train = log_cp_transformer.fit_transform(X_train)
            X_test = log_cp_transformer.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:  
            raise HTTPException(status_code=500, detail=f"Error in log_cp_transformer function during feature engineering: {str(e)}")
    
    def reciprocal_transformer(self, 
                                X_train: pd.DataFrame, 
                                X_test: pd.DataFrame, 
                                dataset: pd.DataFrame, 
                                independent_features: List[str]
                                ):
        
        """
        Handle the reciprocal transformation of the dataset
        """

        logger.info(f"Entered in 'reciprocal_transformer' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            reciprocal_transformer =  ReciprocalTransformer(variables=independent_features)

            X_train = reciprocal_transformer.fit_transform(X_train)
            X_test = reciprocal_transformer.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:      
            raise HTTPException(status_code=500, detail=f"Error in reciprocal_transformer function during feature engineering: {str(e)}")
    
    def square_root_transformer(self, 
                                X_train: pd.DataFrame, 
                                X_test: pd.DataFrame, 
                                dataset: pd.DataFrame, 
                                independent_features: List[str]
                                ):
        
        """
        Handle the square root transformation of the dataset
        """

        logger.info(f"Entered in 'square_root_transformer' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            square_root_transformer =  PowerTransformer(variables=independent_features,
                                                        exp=0.5
                                                        )

            X_train = square_root_transformer.fit_transform(X_train)
            X_test = square_root_transformer.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:      
            raise HTTPException(status_code=500, detail=f"Error in square_root_transformer function during feature engineering: {str(e)}")
    
    def box_cox_transformer(self, 
                            X_train: pd.DataFrame, 
                            X_test: pd.DataFrame, 
                            dataset: pd.DataFrame, 
                            independent_features: List[str]
                            ):
        
        """
        Handle the box cox transformation of the dataset
        """

        logger.info(f"Entered in 'box_cox_transformer' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            box_cox_transformer =  BoxCoxTransformer(variables=independent_features)

            X_train = box_cox_transformer.fit_transform(X_train)
            X_test = box_cox_transformer.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:      
            raise HTTPException(status_code=500, detail=f"Error in box_cox_transformer function during feature engineering: {str(e)}")
    
    def yeo_johnson_transformer(self, 
                                X_train: pd.DataFrame, 
                                X_test: pd.DataFrame, 
                                dataset: pd.DataFrame, 
                                independent_features: List[str]
                                ):
        
        """
        Handle the yeo johnson transformation of the dataset
        """

        logger.info(f"Entered in 'yeo_johnson_transformer' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            yeo_johnson_transformer =  YeoJohnsonTransformer(variables=independent_features)

            X_train = yeo_johnson_transformer.fit_transform(X_train)
            X_test = yeo_johnson_transformer.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:      
            raise HTTPException(status_code=500, detail=f"Error in yeo_johnson_transformer function during feature engineering: {str(e)}")

    def mean_normalization_scaler(self, 
                                  X_train: pd.DataFrame, 
                                  X_test: pd.DataFrame, 
                                  dataset: pd.DataFrame, 
                                  independent_features: List[str]
                                  ):
        
        """
        Handle the mean normalization scaler of the dataset
        """

        logger.info(f"Entered in 'mean_normalization_scaler' function")

        try:

            # Store original index and column order
            original_index = dataset.index
            original_columns = dataset.columns.tolist()

            # Create a copy of dataset without the columns to be imputed
            remaining_cols = [col for col in dataset.columns if col not in independent_features]
            dataset_remaining = dataset[remaining_cols].copy()

            mean_normalization_scaler =  MeanNormalizationScaler(variables=independent_features)

            X_train = mean_normalization_scaler.fit_transform(X_train)
            X_test = mean_normalization_scaler.transform(X_test)

            # Concatenate X_train and X_test vertically and reindex to match original order
            combined_X = pd.concat([X_train, X_test], axis=0)
            combined_X = combined_X.reindex(original_index)

            # Concatenate the combined_X with the remaining columns
            edited_dataset = pd.concat([combined_X, dataset_remaining], axis=1)

            # Reorder columns to match original order
            edited_dataset = edited_dataset[original_columns]

            return edited_dataset
        
        except Exception as e:      
            raise HTTPException(status_code=500, detail=f"Error in mean_normalization_scaler function during feature engineering: {str(e)}")
    
    def datetime_features(self, dataset: pd.DataFrame):
        
        """
        Handle the datetime features of the dataset
        """

        logger.info(f"Entered in 'datetime_features' function")

        try:

            datetime_features =  DatetimeFeatures(variables=None,
                                                  features_to_extract=None
                                                  )

            edited_dataset = datetime_features.fit_transform(dataset)

            return edited_dataset
        
        except Exception as e:      
            raise HTTPException(status_code=500, detail=f"Error in datetime_features function during feature engineering: {str(e)}")
