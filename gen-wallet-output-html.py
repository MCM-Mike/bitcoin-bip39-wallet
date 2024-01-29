#!/usr/bin/env python3
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip49, Bip84, Bip44Coins, Bip49Coins, Bip84Coins
import qrcode
import base64
from io import BytesIO
from datetime import datetime

def get_user_input():
    choice = input("Choose mnemonic length (12 or 24 words): ").strip()
    strength = 128 if choice == "12" else 256
    return strength

def generate_mnemonic(strength):
    mnemo = Mnemonic("english")
    return mnemo.generate(strength)

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    return base64.b64encode(img_buffer.getvalue()).decode()

def create_html(mnemonic, addresses, file_name="mnemonic_and_addresses.html"):
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_name, 'w') as file:
        file.write("<html><body>\n")
        file.write(f"<h1>Wallet Information</h1>\n")
        file.write(f"<p>Generated on: {current_date}</p>\n")
        file.write(f"<h2>Mnemonic</h2>\n<p>{mnemonic}</p>\n")
        mnemonic_qr = generate_qr_code(mnemonic)
        file.write(f"<img src='data:image/png;base64,{mnemonic_qr}' alt='Mnemonic QR Code'><br><br>\n")

        file.write("<h2>Addresses and Public Keys</h2>\n")
        file.write("<table border='1' style='border-collapse: collapse;'>\n")
        file.write("<tr><th>BIP Type</th><th>Address</th><th>Address QR Code</th><th>Public Key</th><th>Public Key QR Code</th></tr>\n")

        for bip_type, data in addresses.items():
            address_qr = generate_qr_code(data["address"])
            pub_key_qr = generate_qr_code(data["pub_key"])
            file.write(f"<tr><td>{bip_type}</td><td>{data['address']}</td><td><img src='data:image/png;base64,{address_qr}' alt='Address QR Code'></td><td>{data['pub_key']}</td><td><img src='data:image/png;base64,{pub_key_qr}' alt='Public Key QR Code'></td></tr>\n")

        file.write("</table>\n</body></html>")

def main():
    strength = get_user_input()
    mnemonic = generate_mnemonic(strength)
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    addresses = {
        "BIP44": {
            "address": Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN).DeriveDefaultPath().PublicKey().ToAddress(),
            "pub_key": Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN).DeriveDefaultPath().PublicKey().ToExtended(),
        },
        "BIP49": {
            "address": Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN).DeriveDefaultPath().PublicKey().ToAddress(),
            "pub_key": Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN).DeriveDefaultPath().PublicKey().ToExtended(),
        },
        "BIP84": {
            "address": Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN).DeriveDefaultPath().PublicKey().ToAddress(),
            "pub_key": Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN).DeriveDefaultPath().PublicKey().ToExtended(),
        },
    }

    create_html(mnemonic, addresses)

if __name__ == "__main__":
    main()
