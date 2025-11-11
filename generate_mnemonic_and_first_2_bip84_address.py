import subprocess
import sys

def install_and_import(package, import_name=None):
    """
    Installs a package if it's not already installed, then imports it.
    """
    if import_name is None:
        import_name = package
    try:
        __import__(import_name)
    except ImportError:
        print(f"'{package}' not found. Installing now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            __import__(import_name)
            print(f"'{package}' installed successfully.")
        except Exception as e:
            print(f"Error installing '{package}': {e}")
            sys.exit(1)

# Check and install dependencies
install_and_import("mnemonic")
install_and_import("bip_utils")

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

