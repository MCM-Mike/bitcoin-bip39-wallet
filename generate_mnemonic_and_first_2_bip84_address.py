import subprocess
import sys
import os

def setup_virtual_environment():
    """
    Sets up a virtual environment, installs dependencies, and ensures the
    script runs within it.
    """
    venv_dir = "venv"
    if sys.prefix == os.path.abspath(venv_dir):
        # Already in the correct virtual environment
        return

    if not os.path.exists(venv_dir):
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

    # Determine the path to the python executable in the venv
    if sys.platform == "win32":
        python_executable = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        python_executable = os.path.join(venv_dir, "bin", "python")

    # Uninstall old fpdf versions and install dependencies
    print("Uninstalling old fpdf versions and installing dependencies...")
    subprocess.check_call([python_executable, "-m", "pip", "uninstall", "--yes", "fpdf", "pypdf"])
    subprocess.check_call([python_executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # Relaunch the script with the venv's python
    print("Relaunching script in the virtual environment...")
    os.execv(python_executable, [python_executable] + sys.argv)

# Setup virtual environment and dependencies before importing them
setup_virtual_environment()

from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip84, Bip84Coins, Bip44Changes

def generate_mnemonic(strength):
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=strength)

def get_seed_bytes(mnemonic):
    return Bip39SeedGenerator(mnemonic).Generate()

def derive_addresses(seed_bytes, n_address_count=2):
    addresses = []
    bip_obj = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
    account = bip_obj.Purpose().Coin().Account(0)
    change = account.Change(Bip44Changes.CHAIN_EXT)
    for i in range(n_address_count):
        address = change.AddressIndex(i).PublicKey().ToAddress()
        addresses.append(address)
    return addresses

def main():
    choice = input("Choose mnemonic length (12 or 24 words): ").strip()
    if choice not in ["12", "24"]:
        print("Invalid choice. Please enter either '12' or '24'.")
        sys.exit(1)
    
    strength = 128 if choice == "12" else 256
    mnemonic = generate_mnemonic(strength)
    print("Generated Mnemonic:", mnemonic)

    seed_bytes = get_seed_bytes(mnemonic)
    addresses = derive_addresses(seed_bytes)

    print("\nFirst two native SegWit addresses:")
    for idx, address in enumerate(addresses, 1):
        print(f"Address {idx}: {address}")

if __name__ == "__main__":
    main()

