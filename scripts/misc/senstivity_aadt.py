import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import seaborn as sns
import geopandas as gpd
import tqdm
import os
import argparse

parser = argparse.ArgumentParser(description="# of Run")
parser.add_argument('--run', type=int, help='Run number')
args = parser.parse_args()

run = args.run

print("Run number: ", run)

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

plt.rcParams['axes.axisbelow'] = True

parent_dir = str(Path(__file__).resolve().parent.parent)

# Add the parent directory to sys.path
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Now you can import the module as if it was in the same directory
import utils.aadt_predictor as ap

NUM_JOBS = int(os.getenv('SLURM_NTASKS')) if os.getenv('SLURM_NTASKS') else -1

### Load data
HPMS_DIR = Path('../../data/processed_data/HPMS')
RANDOM_STATE = None
RESPONSE_VARS = ['AADT_MDV', 'AADT_HDV']
RF_PREDICTOR_VARS = ["STATEFP", "COUNTYFP", "F_SYSTEM", "THROUGH_LANES", "AADT"]

predictor = ap.AADTPredictor(HPMS_DIR / 'hpms_aadt_subset.csv', None, random_state = RANDOM_STATE)
ERROR_SCOPE = np.concatenate([np.arange(0, 0.01, 0.001), np.arange(0.01, 0.1, 0.005)])
results_AADT_perturb = []

for response_var in RESPONSE_VARS:

    predictor.response_var = response_var
    predictor.subset_train_data()

    for error in tqdm.tqdm(ERROR_SCOPE):
            
        predictor.split_data(RF_PREDICTOR_VARS, state_fips= None, test_size=0.2)
        predictor.initialize_model('Random Forest', n_jobs = NUM_JOBS)

        # perturb total AADT
        predictor.X_train['AADT'] = predictor.X_train['AADT'] * (1 +  np.random.uniform(-error, error, predictor.X_train.shape[0]))
        predictor.X_test['AADT'] = predictor.X_test['AADT'] * (1 +  np.random.uniform(-error, error, predictor.X_test.shape[0]))

        predictor.fit_model()

        y_pred = predictor.model.predict(predictor.X_test)

        r2 = r2_score(predictor.y_test, y_pred)
        mse = mean_squared_error(predictor.y_test, y_pred)
        mae = mean_absolute_error(predictor.y_test, y_pred)

        results_AADT_perturb.append({
            'response_var': response_var,
            'error': error,
            'r2': r2,
            'rmse': np.sqrt(mse),
            'mae': mae,
            'run': run
        })

results_AADT_perturb_df = pd.DataFrame(results_AADT_perturb)
results_AADT_perturb_df.to_csv(f'../../data/results/sensitivity_results_AADT_perturb_{run}.csv', index = False)