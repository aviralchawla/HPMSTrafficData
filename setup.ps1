# Install packages from requirements.txt
Write-Host "Installing packages from requirements.txt..."
pip install -r requirements.txt

# Run scripts from the scripts directory
Write-Host "Running scripts..."
Set-Location -Path ./scripts

# Raw Data
python download_raw_data.py
python compile_raw_data.py

# HPMS
python subset_hpms.py
python impute_hpms.py
python joingeo_hpms.py

# Traffic Density
Set-Location -Path ..