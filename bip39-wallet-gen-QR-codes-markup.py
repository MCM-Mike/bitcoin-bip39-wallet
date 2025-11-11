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
install_and_import("qrcode")

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
