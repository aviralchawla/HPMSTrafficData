"""
HPMS Data Paper
by Aviral Chawla, Meg Fay, and Britanny Antonczak

Summary: This script contains the AADTPredictor class that is used to predict the AADT values using the Random Forest and Linear Regression models.

<LICENSE>
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_validate
from sklearn.model_selection import GridSearchCV
from pathlib import Path


class AADTPredictor:
    def __init__(self, data_path: Path, response_var, random_state: int = 42):
        self.data_path = data_path
        self.data = None
        self.data_full = None
        self.response_var = response_var
        self.model = None
        self.random_state = random_state

        self._load_data()

    def _load_data(self):
        """
        Summary: Load the AADT subset data
        """
        print(f"Loading data from {self.data_path}", flush=True)
        try:
            self.data_full = pd.read_csv(self.data_path)
            print(
                f"Full Data loaded successfully: {self.data_full.shape[0]} rows and {self.data_full.shape[1]} columns.",
                flush=True,
            )
            self._pre_process_data()
            print(
                f"Training Data loaded successfully: {self.data.shape[0]} rows and {self.data.shape[1]} columns.",
                flush=True,
            )

        except Exception as e:
            print(f"ERROR: The data could not be loaded. {e}", flush=True)

    def _pre_process_data(self):
        """
        Summary: Set the data types for the columns
        """
        if self.data_full is not None:
            try:
                print("Pre-processing data...", flush=True)
                self.data_full = self.data_full.astype(
                    {
                        "STATEFP": "str",
                        "COUNTYFP": "str",
                        "GEOID": "str",
                        "F_SYSTEM": "category",
                        "URBAN": "category",
                    }
                )
                self.data_full["STATEFP"] = self.data_full["STATEFP"].str.pad(
                    2, side="left", fillchar="0"
                )
                self.data_full["COUNTYFP"] = self.data_full["COUNTYFP"].str.pad(
                    3, side="left", fillchar="0"
                )
                self.data_full["GEOID"] = self.data_full["GEOID"].str.pad(
                    5, side="left", fillchar="0"
                )

                self.subset_train_data()
            except Exception as e:
                print(f"ERROR: The data could not be pre-processed. {e}", flush=True)
        else:
            print("ERROR: The data is empty.", flush=True)

    def subset_train_data(self):
        """
        Summary: Subset the training data by removing rows with missing response variables
        """
        try:
            # Drop rows with missing response variables
            self.data = self.data_full.dropna(subset=[self.response_var], inplace=False)
            print(
                f"Training Data subsetted successfully with {self.response_var}: {self.data.shape[0]} rows and {self.data.shape[1]} columns.",
                flush=True,
            )
        except Exception as e:
            print(f"ERROR: The data could not be subsetted. {e}", flush=True)

    def split_data(
        self, predictor_vars, test_size=0.2, state_fips=None, stratify_by_state=False
    ):
        """
        Summary: Split the data into training and testing sets
        Input:
            - response_var (str): The response variable
            - predictor_vars (list): The predictor variables
            - test_size (float): The proportion of the data to include in the test split
            - state_fips (str): The state FIPS code to split the data by
            - stratify_by_state (bool): Whether to stratify the data by state
        """
        print(
            f"Training and testing data split with test size {test_size} on State {state_fips} and {'not' if not stratify_by_state else ''} stratified ...",
            flush=True,
        )
        if state_fips:
            try:
                data = self.data[self.data["STATEFP"] == state_fips]
            except Exception as e:
                print(f"ERROR: The data could not be split by state. {e}", flush=True)
        else:
            data = self.data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            data[predictor_vars],
            data[self.response_var],
            test_size=test_size,
            random_state=self.random_state,
            shuffle=True,
            stratify=data["STATEFP"] if stratify_by_state else None,
        )

    def initialize_model(self, model_type, **kwargs):
        """
        Summary: Initialize the selected model
        Input:
            - model_type (str): The type of model to use. Supported models are "Random Forest" and "Linear Regression"
            - **kwargs: Additional keyword arguments to pass to the model
        """
        model_dict = {
            "Random Forest": RandomForestRegressor,
            "Linear": LinearRegression,
        }
        try:
            self.model = model_dict[model_type](**kwargs)
            print(f"{model_type} model initialized with- {kwargs}", flush=True)
        except Exception as e:
            print(f"ERROR: The model could not be initialized. {e}", flush=True)

    def fit_model(self):
        """
        Summary: Fit the model to the data
        """
        try:
            self.model.fit(self.X_train, self.y_train)
            print("Model trained successfully", flush=True)
        except Exception as e:
            print(f"ERROR: The model could not be trained. {e}", flush=True)

    def test_model(self):
        """
        Summary: Test the model
        Output:
            - r2 (float): The R-squared value
            - mae (float): The mean absolute error
            - mse (float): The mean squared error
        """
        y_pred = self.model.predict(self.X_test)
        r2 = r2_score(self.y_test, y_pred)
        mae = mean_absolute_error(self.y_test, y_pred)
        mse = mean_squared_error(self.y_test, y_pred)
        return r2, mae, mse

    def cross_validate_model(self, n_splits):
        """
        Summary: Cross validate the model
        Input:
            - n_splits (int): The number of splits to use
        Output:
            - r2_scores (list): The R-squared scores
            - mae_scores (list): The mean absolute error scores
            - mse_scores (list): The mean squared error scores
        """
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=self.random_state)
        model_cv = cross_validate(
            self.model,
            self.X_train,
            self.y_train,
            cv=cv,
            scoring=("r2", "neg_mean_absolute_error", "neg_mean_squared_error"),
            return_estimator=True,
            n_jobs=-1,
        )
        r2_scores = model_cv["test_r2"]
        mae_scores = -model_cv["test_neg_mean_absolute_error"]
        mse_scores = -model_cv["test_neg_mean_squared_error"]

        return r2_scores, mae_scores, mse_scores

    def hyperparameter_tuning(self, param_grid, n_splits):
        """
        Summary: Tune the hyperparameters of the model
        Input:
            - param_grid (dict): The hyperparameter grid
            - n_splits (int): The number of splits to use
        Output:
            - best_params (dict): The best hyperparameters
            - best_estimator: The best estimator
            - cv_results (DataFrame): The cross-validation results
        """
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=self.random_state)
        grid_search = GridSearchCV(
            self.model, param_grid, cv=cv, n_jobs=-1, scoring="neg_mean_squared_error"
        )
        grid_search.fit(self.X_train, self.y_train)
        best_params = grid_search.best_params_
        best_estimator = grid_search.best_estimator_
        cv_results = pd.DataFrame(grid_search.cv_results_)
        return best_params, best_estimator, cv_results
