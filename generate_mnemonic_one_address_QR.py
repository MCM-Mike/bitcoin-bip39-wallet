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
install_and_import("fpdf")

from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip84, Bip84Coins, Bip44Changes
import qrcode
from fpdf import FPDF
from datetime import datetime

def generate_mnemonic(strength):
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=strength)

def get_seed_bytes(mnemonic):
    return Bip39SeedGenerator(mnemonic).Generate()

def derive_address(seed_bytes):
    bip_obj = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
    account = bip_obj.Purpose().Coin().Account(0)
    change = account.Change(Bip44Changes.CHAIN_EXT)
    address = change.AddressIndex(0).PublicKey().ToAddress()
    return address

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def create_larger_card(mnemonic, address, qr_img):
    pdf = FPDF(orientation='P', unit='in', format=(4, 5))  # Adjusted size
    pdf.add_page()
    pdf.set_font('Arial', '', 10)

    # Add numbered mnemonic
    pdf.set_xy(0.1, 0.1)
    mnemonic_words = mnemonic.split()
    mnemonic_text = "\n".join(f"{i+1}. {word}" for i, word in enumerate(mnemonic_words))
    pdf.multi_cell(3.8, 0.15, f'Mnemonic Words:\n{mnemonic_text}', align='L')

    # Position for the Bitcoin address moved up slightly more (10% closer)
    address_start_y = 2.9  # Further adjustment to bring the address closer to the mnemonic
    pdf.set_xy(0.1, address_start_y)
    pdf.set_font('Arial', '', 6)

    # Add the first Bitcoin address
    pdf.cell(0, 0.10, f'Address: {address}', ln=1)

    # Add QR code for the first address, positioned accordingly
    qr_img.save("temp_qr.png")
    pdf.image("temp_qr.png", x=0.1, y=address_start_y + 0.15, w=0.7, h=0.7)

    # Date of creation, positioned just below the QR code
    pdf.set_xy(0.1, address_start_y + 0.9)
    pdf.set_font('Arial', '', 5)
    pdf.cell(0, 0.10, f'Created on: {datetime.now().strftime("%Y-%m-%d")}', ln=1)

    # Save PDF
    pdf.output("larger_card.pdf")

def main():
    choice = input("Choose mnemonic length (12 or 24 words): ").strip()
    if choice not in ["12", "24"]:
        print("Invalid choice. Please enter either '12' or '24'.")
        sys.exit(1)
    
    strength = 128 if choice == "12" else 256
    mnemonic = generate_mnemonic(strength)
    seed_bytes = get_seed_bytes(mnemonic)
    address = derive_address(seed_bytes)
    qr_img = generate_qr_code(address)

    create_larger_card(mnemonic, address, qr_img)
    print("Larger card PDF has been created with the mnemonic and Bitcoin address.")

if __name__ == "__main__":
    main()
