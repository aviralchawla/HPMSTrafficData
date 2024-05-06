from pathlib import Path
import utils.aadt_predictor as ap
import tqdm

def main():

    HPMS_DIR = Path('../data/processed_data/HPMS')
    RESPONSE_VARS = ['AADT_MDV', 'AADT_HDV']
    RF_PREDICTOR_VARS = ["COUNTYFP", "F_SYSTEM", "THROUGH_LANES", "AADT"]
    RANDOM_STATE = 42

    predictor = ap.AADTPredictor(HPMS_DIR / 'hpms_aadt_subset.csv', None, random_state = RANDOM_STATE)

    for response_var in tqdm.tqdm(RESPONSE_VARS):
        predictor.response_var = response_var
        predictor.subset_train_data()
        predictor.split_data(RF_PREDICTOR_VARS, state_fips= None, test_size=1e-10)
        predictor.initialize_model("Random Forest")
        predictor.fit_model()

        missing_data = predictor.data_full[predictor.data_full[response_var].isna()]

        try:
            predictor.data_full.loc[missing_data.index, response_var] = predictor.model.predict(missing_data[RF_PREDICTOR_VARS])
            print(f"Imputed {missing_data.shape[0]} missing values for {response_var}", flush=True)
        except Exception as e:
            print(f"ERROR: Could not impute missing values for {response_var}. {e}", flush=True)
    
    predictor.data_full.to_csv(HPMS_DIR / 'hpms_aadt_imputed.csv', index=False)

if __name__ == '__main__':
    main()