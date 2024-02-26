"""
Code to run the Random Forest Regression model on HPMS data
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_validate
from sklearn.model_selection import GridSearchCV

class AADTPredictor:
    def __init__(self, data_path, response_vars, random_state = 42, outdir="./"):
        self.data_path = data_path
        self.data = None
        self.response_vars = response_vars
        self.outdir = outdir
        self.model = None
        self.random_state = random_state

        self.load_data()

    def load_data(self):
        """
        Load the data
        """
        print(f"Loading data from {self.data_path}", flush=True)
        try:
            self.data = pd.read_csv(self.data_path)
            self.pre_process_data()
            print(f"Data loaded successfully: {self.data.shape[0]} rows and {self.data.shape[1]} columns.", flush=True)
        except Exception as e:
            print(f"ERROR: The data could not be loaded. {e}", flush=True)

    def pre_process_data(self):
        """
        Set the data types for the columns
        """
        if self.data is not None:
            try:
                print("Pre-processing data...", flush=True)
                self.data = self.data.astype({
                    'STATEFP': 'str', 
                    'COUNTYFP': 'str', 
                    'GEOID': 'str', 
                    'F_SYSTEM': 
                    'category', 
                    'URBAN': 'category'
                    })
                self.data["STATEFP"] = self.data["STATEFP"].str.pad(2, side ='left', fillchar = '0')
                self.data["COUNTYFP"] = self.data["COUNTYFP"].str.pad(3, side ='left', fillchar = '0')
                self.data["GEOID"] = self.data["GEOID"].str.pad(5, side ='left', fillchar = '0')

                # Drop rows with missing response variables
                self.data.dropna(subset=self.response_vars, inplace=True)
            except Exception as e:
                print(f"ERROR: The data could not be pre-processed. {e}", flush=True)
        else:
            print("ERROR: The data is empty.", flush=True)
    
    def split_data(self, response_var, predictor_vars, test_size=0.2, state_fips = None, stratify_by_state = False):
        """
        Split the data into training and testing sets

        Args:
        response_var (str): The response variable
        predictor_vars (list): The predictor variables
        test_size (float): The proportion of the data to include in the test split
        """
        print(f"Training and testing data split with test size {test_size} on State {state_fips} and {'not' if not stratify_by_state else ''} stratified ...", flush=True)
        if state_fips:
            try:
                data = self.data[self.data['STATEFP'] == state_fips]
            except Exception as e:
                print(f"ERROR: The data could not be split by state. {e}", flush=True)
        else:
            data = self.data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            data[predictor_vars], 
            data[response_var], 
            test_size=test_size,
            random_state=self.random_state,
            shuffle=True,
            stratify= data["STATEFP"] if stratify_by_state else None
            )

    def initialize_model(self, model_type, **kwargs):
        """
        Initialize the model

        Args:
        model_type (str): The type of model to use. Supported models are "Random Forest" and "Linear Regression"

        Keyword Args:
        **kwargs: Additional keyword arguments to pass to the model
        """
        model_dict = {
            "Random Forest": RandomForestRegressor,
            "Linear": LinearRegression
        }
        try:
            self.model = model_dict[model_type](**kwargs)
            print(f"{model_type} model initialized with- {kwargs}", flush=True)
        except Exception as e:
            print(f"ERROR: The model could not be initialized. {e}", flush=True)
    
    def fit_model(self):
        """
        Train the model
        """
        self.model.fit(self.X_train, self.y_train)

    def test_model(self):
        """
        Test the model
        """
        y_pred = self.model.predict(self.X_test)
        r2 = r2_score(self.y_test, y_pred)
        mae = mean_absolute_error(self.y_test, y_pred)
        mse = mean_squared_error(self.y_test, y_pred)
        return r2, mae, mse
    
    def validate_model(self, n_splits):
        """
        Cross validate the model

        Args:
        n_splits (int): The number of splits to use
        """
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=self.random_state)
        model_cv = cross_validate(self.model, self.X_train, self.y_train, cv=cv, scoring=('r2', 'neg_mean_absolute_error', 'neg_mean_squared_error'),  return_estimator=True, n_jobs=-1)
        r2_scores = model_cv['test_r2']
        mae_scores = -model_cv['test_neg_mean_absolute_error']
        mse_scores = -model_cv['test_neg_mean_squared_error']

        return r2_scores, mae_scores, mse_scores
    
    def hyperparameter_tuning(self, param_grid, n_splits):
        """
        Tune the hyperparameters of the model

        Args:
        param_grid (dict): The hyperparameter grid
        n_splits (int): The number of splits to use
        """
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=self.random_state)
        grid_search = GridSearchCV(self.model, param_grid, cv=cv, n_jobs=-1, scoring='neg_mean_squared_error')
        grid_search.fit(self.X_train, self.y_train)
        best_params = grid_search.best_params_
        best_estimator = grid_search.best_estimator_
        cv_results = pd.DataFrame(grid_search.cv_results_)
        return best_params, best_estimator, cv_results
