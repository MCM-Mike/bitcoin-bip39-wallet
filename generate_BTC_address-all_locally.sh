#!/bin/bash

# Variables
now=$(date)

# Define Python script content
read -r -d '' PYTHON_SCRIPT << EOF
from bit import Key
from Crypto.Hash import RIPEMD160
import hashlib
import base58
from bip_utils import Bip44, Bip49, Bip84, Bip44Coins, Bip49Coins, Bip84Coins, Bip39SeedGenerator

def generate_bitcoin_address():
    # Generate a new Bitcoin wallet
    wallet = Key()

    # Extract the public key
    public_key = wallet.public_key

    # Perform SHA-256 hashing on the public key
    sha256 = hashlib.sha256()
    sha256.update(public_key)
    sha_result = sha256.digest()

    # Perform RIPEMD-160 hashing on the result
    ripemd = RIPEMD160.new()
    ripemd.update(sha_result)
    ripemd_result = ripemd.digest()

    # Add version byte (0x00 for Bitcoin Mainnet)
    versioned_payload = b'\x00' + ripemd_result

    # Double SHA-256 hash the versioned payload
    checksum_full = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()

    # Take the first 4 bytes of the second SHA-256 hash as the checksum
    checksum = checksum_full[:4]

    # Add the checksum to the versioned payload
    full_payload = versioned_payload + checksum

    # Encode the full payload using Base58
    bitcoin_address = base58.b58encode(full_payload).decode('utf-8')

    return bitcoin_address, wallet

def generate_bip_addresses_and_keys(mnemonic):
    # Generate seed from mnemonic
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    # Generate BIP44, BIP49, BIP84 addresses and private keys
    bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    bip44_address = bip44.PublicKey().ToAddress()
    bip44_private_key = bip44.PrivateKey().ToWif()

    bip49 = Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN)
    bip49_address = bip49.PublicKey().ToAddress()
    bip49_private_key = bip49.PrivateKey().ToWif()

    bip84 = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
    bip84_address = bip84.PublicKey().ToAddress()
    bip84_private_key = bip84.PrivateKey().ToWif()

    return {
        'BIP44': {'address': bip44_address, 'private_key': bip44_private_key},
        'BIP49': {'address': bip49_address, 'private_key': bip49_private_key},
        'BIP84': {'address': bip84_address, 'private_key': bip84_private_key}
    }

# Generate and print the Bitcoin address and retrieve wallet object
bitcoin_address, wallet = generate_bitcoin_address()
print("Bitcoin Address:", bitcoin_address)
print("Private Key:", wallet.to_wif())

# Example mnemonic, replace with actual mnemonic for real use
mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
bip_addresses_keys = generate_bip_addresses_and_keys(mnemonic)
for bip_type, data in bip_addresses_keys.items():
    print(f"{bip_type} Address: {data['address']}")
    print(f"{bip_type} Private Key: {data['private_key']}")

EOF


# Create a temporary Python environment
current_date=$(date +"%Y%m%d_%H%M")
env_dir="/tmp/${current_date}"
mkdir -p "$env_dir"
python3 -m venv "$env_dir/venv"
source "$env_dir/venv/bin/activate"
pip install bit Crypto fpdf bip-utils base58

# Write Python script to a temporary file and execute it
python_script_file="${env_dir}/script.py"
echo "$PYTHON_SCRIPT" > "$python_script_file"
echo -e "\n \n \n"

# ASCII Art Header
echo "****************************************************"
echo "*                                                  *"
echo "*            BITCOIN ADDRESS INFORMATION           *"
echo "*                                                  *"
echo "*            $now           *"
echo "****************************************************"
echo

#execute the python code between EOF
python "$python_script_file"

# ASCII Art Footer
echo -e "\n"
echo "****************************************************"
echo "*                                                  *"
echo "*               END OF INFORMATION                *"
echo "*                                                  *"
echo "****************************************************"
echo
echo $date

# Additional Notes or Instructions (Optional)
echo "IMPORTANT: Keep your private keys secure and never share them with anyone."
echo "           This information is confidential and should be handled carefully."

echo -e "\n"
# Clean up
deactivate
rm -rf "$env_dir"
