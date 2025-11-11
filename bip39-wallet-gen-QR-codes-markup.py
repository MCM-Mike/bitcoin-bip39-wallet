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
from bip_utils import Bip39SeedGenerator, Bip44, Bip49, Bip84, Bip44Coins, Bip49Coins, Bip84Coins, Bip44Changes
from datetime import datetime
import qrcode
import base64
from io import BytesIO

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,  # Reduced from 10 to 5
        border=2,    # Reduced from 4 to 2
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    return base64.b64encode(img_buffer.getvalue()).decode()


def get_user_input():
    strength_choice = input("Choose mnemonic length (12 or 24 words): ").strip()
    strength = 128 if strength_choice == "12" else 256
    seed_name = input("Enter a name for the seed (optional): ").strip()
    return strength, seed_name

def generate_mnemonic(strength):
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=strength)


def derive_keys_and_write_to_file(mnemonic, seed_name):
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    date_time_now = datetime.now().strftime("%d%m%Y_%H%M")
    file_name = f"{seed_name}_{date_time_now}.seed" if seed_name else f"{date_time_now}.seed"

    with open(file_name, "w") as file:
        file.write(f"# Seed Information - Generated on {date_time_now}\n")
        if seed_name:
            file.write(f"## Seed Name: {seed_name}\n\n")

        mnemonic_words = mnemonic.split()
        file.write("### Mnemonic Words:\n")
        for i, word in enumerate(mnemonic_words, start=1):
            file.write(f"{i}. {word}\n")

        mnemonic_qr = generate_qr_code(mnemonic)
        file.write("\n### Mnemonic QR Code:\n")
        file.write(f"![](data:image/png;base64,{mnemonic_qr})\n\n")
        file.write("| BIP Type | Description | Root Key |\n")
        file.write("|----------|-------------|----------|\n")

        bip_descriptions = {
            'BIP44': 'Legacy',
            'BIP49': 'Segwit Compatible',
            'BIP84': 'Segwit Native'
        }

        for bip_type, bip_cls, coin_type in [('BIP44', Bip44, Bip44Coins.BITCOIN), ('BIP49', Bip49, Bip49Coins.BITCOIN), ('BIP84', Bip84, Bip84Coins.BITCOIN)]:
            bip_obj = bip_cls.FromSeed(seed_bytes, coin_type)
            root_key = bip_obj.PrivateKey().ToExtended()
            file.write(f"| {bip_type} | {bip_descriptions[bip_type]} | {root_key} |\n")

        # Account Extended Public Keys and QR Codes
        file.write("\n## Account Extended Public Keys\n")
        file.write("| BIP Type | Account Extended Public Key | QR Code | Notes |\n")
        file.write("|----------|------------------------------|---------|-------|\n")
        
        for bip_type, bip_cls, coin_type in [('BIP44', Bip44, Bip44Coins.BITCOIN), ('BIP49', Bip49, Bip49Coins.BITCOIN), ('BIP84', Bip84, Bip84Coins.BITCOIN)]:
            bip_obj = bip_cls.FromSeed(seed_bytes, coin_type)
            account_ext_pub_key = bip_obj.Purpose().Coin().Account(0).PublicKey().ToExtended()
            account_ext_pub_key_qr = generate_qr_code(account_ext_pub_key)
            file.write(f"| {bip_type} | {account_ext_pub_key} | ![](data:image/png;base64,{account_ext_pub_key_qr}) |  |\n")

        # Derived Addresses and QR Codes
        file.write("\n## Derived Addresses\n")
        file.write("| BIP Type | Address Index | Address | QR Code | Notes |\n")
        file.write("|----------|---------------|---------|---------|-------|\n")

        for bip_type, bip_cls, coin_type in [('BIP44', Bip44, Bip44Coins.BITCOIN), ('BIP49', Bip49, Bip49Coins.BITCOIN), ('BIP84', Bip84, Bip84Coins.BITCOIN)]:
            bip_obj = bip_cls.FromSeed(seed_bytes, coin_type)
            for i in range(3):
                address = bip_obj.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i).PublicKey().ToAddress()
                address_qr_code = generate_qr_code(address)
                file.write(f"| {bip_type} | {i} | {address} | ![](data:image/png;base64,{address_qr_code}) |  |\n")

    print(f"Seed information written to {file_name}")

def main():
    strength, seed_name = get_user_input()
    mnemonic = generate_mnemonic(strength)
    derive_keys_and_write_to_file(mnemonic, seed_name)

if __name__ == "__main__":
    main()
