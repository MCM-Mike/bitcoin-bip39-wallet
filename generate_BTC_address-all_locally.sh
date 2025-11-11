#!/usr/bin/env bash
set -e

# Variables
now=$(date)

# Create a temporary Python environment
current_date=$(date +"%Y%m%d_%H%M")
env_dir="/tmp/${current_date}"
echo "Creating temporary directory..."
mkdir -p "$env_dir"
echo "Creating Python virtual environment..."
python3 -m venv "$env_dir/venv"
echo "Installing Python dependencies..."
"$env_dir/venv/bin/pip" install bit pycryptodome fpdf bip_utils base58
echo "Dependencies installed."

# ASCII Art Header
echo "****************************************************"
echo "*                                                  *"
echo "*            BITCOIN ADDRESS INFORMATION           *"
echo "*                                                  *"
echo "*            ${now}           *"
echo "****************************************************"
echo

#execute the python code
echo "Executing Python script..."
"$env_dir/venv/bin/python" "temp_btc_generator.py"
echo "Python script executed."

# ASCII Art Footer
echo -e "\n"
echo "****************************************************"
echo "*                                                  *"
echo "*               END OF INFORMATION                *"
echo "*                                                  *"
echo "****************************************************"
echo
echo "$now"

# Additional Notes or Instructions (Optional)
echo "IMPORTANT: Keep your private keys secure and never share them with anyone."
echo "           This information is confidential and should be handled carefully."

echo -e "\n"
# Clean up
echo "Cleaning up..."
rm -rf "$env_dir"
echo "Cleanup complete."
