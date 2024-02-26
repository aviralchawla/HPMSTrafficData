from aadt_predictor import AADTPredictor

OUTDIR = "/"
DATA_DIR = "../data/hpms_aadt_subset.csv"
RESPONSE_VARS = ['AADT_MDV', 'AADT_HDV']
RF_PREDICTOR_VARS = ["STATEFP", "COUNTYFP", "F_SYSTEM", "THROUGH_LANES", "AADT"]
LR_PREDICTOR_VARS = ["THROUGH_LANES", "AADT"]
RANDOM_STATE = 42

predictor = AADTPredictor(DATA_DIR)


