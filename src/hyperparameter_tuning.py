import aadt_predictor as ap
import pickle as pkl
import time

start = time.time()

print("Running tests for Hyperparameter Tuning", flush=True)

OUTDIR = "../results"
DATA_DIR = "../data/hpms_aadt_subset.csv"
RESPONSE_VARS = ['AADT_MDV', 'AADT_HDV']
RF_PREDICTOR_VARS = ["STATEFP", "COUNTYFP", "F_SYSTEM", "THROUGH_LANES", "AADT"]
RANDOM_STATE = 42

param_grid = {
    'n_estimators': [50, 100, 150, 200],
    'max_depth': [5, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

target_states = ["56", "51", "06"]

predictor = ap.AADTPredictor(DATA_DIR, RESPONSE_VARS, outdir = OUTDIR, random_state = RANDOM_STATE)

results = []
for state in target_states:
    for response_var in RESPONSE_VARS:
        print(f"Hyperparameter tuning for {response_var} in state {state}", flush=True)
        predictor.split_data(response_var, RF_PREDICTOR_VARS, state_fips = state)
        predictor.initialize_model("Random Forest")
        best_params, best_estimator, cv_results = predictor.hyperparameter_tuning(param_grid, n_splits=5)
        print(f"Best parameters: {best_params}, Best estimator: {best_estimator}, and CV results: {cv_results}", flush=True)
        results.append({
            "state": state,
            "response_var": response_var,
            "best_params": best_params,
            "best_estimator": best_estimator,
            "cv_results": cv_results
        })

with open(f"{OUTDIR}/hyperparameter_tuning_results.pkl", "wb") as f:
    pkl.dump(results, f)

print("Hyperparameter tuning tests completed", flush=True)
print(f"Time taken: {time.time() - start} seconds", flush=True)