import sys
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from skopt import BayesSearchCV
from skopt.space import Real, Categorical, Integer
from skopt.plots import plot_objective, plot_histogram
import matplotlib.pyplot as plt

# Get the absolute path of the parent directory
parent_dir = str(Path(__file__).resolve().parent.parent)
# parent_dir = str(Path().cwd().parent)

# Add the parent directory to sys.path
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import utils.aadt_predictor as ap

def main():

    HPMS_DIR = Path('../../data/processed_data/HPMS')
    RANDOM_STATE = 42

    NUM_ITERS = 48
    NUM_JOBS = 48
    
    RESPONSE_VARS = ['AADT_MDV', 'AADT_HDV']
    RF_PREDICTOR_VARS = ["STATEFP", "COUNTYFP", "F_SYSTEM", "THROUGH_LANES", "AADT"]

    # load predictor + data
    predictor = ap.AADTPredictor(HPMS_DIR / 'hpms_aadt_subset.csv', None, random_state = RANDOM_STATE)

    for response_var in RESPONSE_VARS:
        print('Tuning hyperparameters for ', response_var)

        # subset data
        predictor.response_var = response_var
        predictor.subset_train_data()
        predictor.split_data(RF_PREDICTOR_VARS, state_fips = None, test_size = 1e-10)

        X, y = predictor.X_train, predictor.y_train

        # Define the parameter space for the Random Forest
        param_space = {
            'n_estimators': Integer(10, 100),
            'max_depth': Integer(5, 50),
            'min_samples_split': Real(0.01, 0.1),
            'min_samples_leaf': Integer(1, 10),
            'max_features': Categorical([None, 'sqrt', 'log2'])
        }

        rf = RandomForestRegressor(random_state=RANDOM_STATE)

        # Setup the BayesSearchCV with the parameter space and the regressor
        opt = BayesSearchCV(
            estimator=rf,
            search_spaces = param_space,
            scoring = 'neg_root_mean_squared_error',  # Use RMSE for scoring
            n_iter = NUM_ITERS,
            cv = 3,  # Number of cross-validation folds
            n_jobs = NUM_JOBS,  # Number of jobs to run in parallel
            random_state = 42
        )

        # Fit the model
        opt.fit(X, y)

        # Best model found
        print("Best parameters found:", opt.best_params_)
        print("Best cross-validation score:", opt.best_score_)

        # Save the best parameters
        with open(f'../../log/best_params_{response_var}.txt', 'w') as f:
            f.write(str(opt.best_params_))

        # show trajectory of search
        results = opt.cv_results_

        # visualize rmse over iterations
        plt.plot(results['mean_test_score'])
        plt.xlabel('Iteration')
        plt.ylabel('Mean RMSE')
        plt.title(f'Bayes Search for Random Forest- {response_var}')
        plt.tight_layout()
        plt.savefig(f'../../figs/hyperparameter_tuning_iter_{response_var}.png', dpi=300)

        # visualize the objective
        _ = plot_objective(opt.optimizer_results_[0])
        plt.suptitle(f'Partial Dependence of RMSE on Hyperparameters - {response_var}')
        plt.tight_layout()
        plt.savefig(f'../../figs/hyperparameter_tuning_objective_{response_var}.png', dpi=300)

        # visualize the histogram of the parameters
        _ = plot_histogram(opt.optimizer_results_[0])
        plt.suptitle(f'Hyperparameter Histogram - {response_var}')
        plt.tight_layout()
        plt.savefig(f'../../figs/hyperparameter_tuning_histogram_{response_var}.png', dpi=300)

if __name__ == "__main__":
    main()