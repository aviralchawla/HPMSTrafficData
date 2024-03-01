import aadt_predictor as ap
import aadt_predictor as ap
import time

start = time.time()

print("Imputing missing AADT values", flush=True)

OUTDIR = "../data"
DATA_DIR = "../data/hpms_aadt_subset.csv"
RESPONSE_VARS = ['AADT_MDV', 'AADT_HDV']
RF_PREDICTOR_VARS = ["COUNTYFP", "F_SYSTEM", "THROUGH_LANES", "AADT"]
RANDOM_STATE = 42

predictor = ap.AADTPredictor(DATA_DIR, None, outdir = OUTDIR, random_state = RANDOM_STATE)

for response_var in RESPONSE_VARS:
    for state in predictor.data_full.STATEFP.unique():
        print(f"Imputing {response_var} for state {state}", flush=True)
        predictor.response_var = response_var
        predictor.subset_train_data()
        predictor.split_data(RF_PREDICTOR_VARS, state_fips = state, test_size=1e-10)
        predictor.initialize_model("Random Forest")
        predictor.fit_model()
        missing_data = predictor.data_full[(predictor.data_full.STATEFP == state) & (predictor.data_full[response_var].isna())]
        try:
            predictor.data_full.loc[missing_data.index, response_var] = predictor.model.predict(missing_data[RF_PREDICTOR_VARS])
            print(f"Imputed {missing_data.shape[0]} missing values for state {state}", flush=True)
        except Exception as e:
            print(f"ERROR: Could not impute missing values for state {state}. {e}", flush=True)

# print count of empty AADT_MDV and AADT_HDV values
print(f"Empty AADT_MDV: {predictor.data_full[predictor.data_full.AADT_MDV.isna()].shape[0]}", flush=True)
print(f"Empty AADT_HDV: {predictor.data_full[predictor.data_full.AADT_HDV.isna()].shape[0]}", flush=True)

predictor.data_full.to_csv(f"{OUTDIR}/hpms_aadt_imputed.csv", index=False)

print("Imputation completed", flush=True)
print(f"Time taken: {time.time() - start} seconds", flush=True)