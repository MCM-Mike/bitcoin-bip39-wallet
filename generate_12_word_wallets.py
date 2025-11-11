import os
import sys
import subprocess
import qrcode
import base64
from io import BytesIO
from datetime import datetime
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip84, Bip84Coins, Bip44Changes

VENV_DIR = "venv_paper_wallet"

def setup_virtual_env():
    """Create a virtual environment and install dependencies."""
    if not os.path.exists(VENV_DIR):
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])

    pip_executable = os.path.join(VENV_DIR, 'bin', 'pip')
    
    # Install dependencies
    dependencies = ["mnemonic", "bip-utils", "qrcode", "Pillow"]
    print("Installing dependencies...")
    for dependency in dependencies:
        subprocess.check_call([pip_executable, "install", dependency])

def generate_seed_phrase_and_address(word_count):
    """
    Generates a BIP39 seed phrase, the first Native SegWit (BIP84) address, and a QR code for the address.
    """
    strength = 128
    mnemo = Mnemonic("english")
    seed_phrase = mnemo.generate(strength=strength)
    
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip84_mst = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
    bip84_acc = bip84_mst.Purpose().Coin().Account(0)
    # Get the change object
    bip84_change = bip84_acc.Change(Bip44Changes.CHAIN_EXT)
    
    # Derive the address at index 0
    bip84_addr_idx = bip84_change.AddressIndex(0)
    address = bip84_addr_idx.PublicKey().ToAddress()

    # Manually construct the derivation path string for the first address
    derivation_path = "m/84'/0'/0'/0/0"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=2,
    )
    qr.add_data(address)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return seed_phrase.split(), address, img_str, derivation_path

def generate_html_output(title, wallets_12_words):
    """
    Generates an HTML string to display the wallets for printing.
    """
    
    def get_wallet_html(wallet_data):
        seed_phrase, address, qr_code, derivation_path, timestamp = wallet_data
        
        words_html = "".join([f"<div class='word'><span>{i+1}.</span> {word}</div>" for i, word in enumerate(seed_phrase)])
        
        return f"""
        <div class="wallet">
            <h3 class="wallet-title">Bitcoin Paper Wallet</h3>
            <div class="seed_phrase">
                {words_html}
            </div>
            <div class="address_container">
                <p class="derivation">Derivation Path (BIP84): {derivation_path}</p>
                <img src="data:image/png;base64,{qr_code}" alt="QR Code" class="qr_code">
                <p class="address">{address}</p>
                <p class="bip39-standard">BIP39 Standard Wallet - {timestamp[:4]}</p>
                <p class="timestamp">Created: {timestamp}</p>
            </div>
        </div>
        """
        
    def generate_page(wallets, page_title, wallets_per_row):
        wallet_html_parts = [get_wallet_html(wallet) for wallet in wallets]
        
        pages_html = ""
        for i in range(0, len(wallet_html_parts), 2):
            row_item1 = wallet_html_parts[i]
            row_item2 = wallet_html_parts[i+1] if (i+1) < len(wallet_html_parts) else '<div class="wallet"></div>'
            pages_html += f'<div class="page"><h2 class="page-title">{page_title}</h2><div class="wallet-row">{row_item1}{row_item2}</div></div>'

        return pages_html
        
    html_12 = generate_page(wallets_12_words, "12-Word Seed Phrases", 2)

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
            @media print {{
                body {{ -webkit-print-color-adjust: exact; }}
                .page {{ page-break-after: always; }}
            }}
            body {{ font-family: 'Roboto Mono', monospace; margin: 20px; }}
            .page {{ width: 210mm; height: 297mm; margin: auto; border: 1px solid #ccc; padding: 10mm; box-sizing: border-box; }}
            .page-title {{ text-align: center; font-size: 20px; margin-bottom: 20px; }}
            h1 {{ text-align: center; }}
            .wallet-row {{ display: flex; justify-content: space-between; }}
            .wallet {{ border: 1px solid black; padding: 10px; box-sizing: border-box; display: flex; flex-direction: column; }}
            .wallet-row .wallet {{ width: 48%; }}
            .seed_phrase {{ display: flex; flex-wrap: wrap; width: 100%; margin-bottom: 10px;}}
            .word {{ width: 50%; font-size: 14px; margin-bottom: 4px;}}
            .word span {{ font-weight: bold; margin-right: 5px; }}
            .address_container {{ width: 100%; text-align: center; border-top: 1px solid #ccc; padding-top: 10px; }}
            .qr_code {{ width: 100px; height: 100px; margin: 0 auto 10px auto; }}
            .address {{ font-size: 14px; word-wrap: break-word; font-weight: bold;}}
            .bip39-standard {{ font-size: 10px; margin-top: 10px; }}
            .derivation {{ font-size: 10px; margin-bottom: 5px; }}
            .timestamp {{ font-size: 10px; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {html_12}
    </body>
    </html>
    """
    
    return html

def main_script():
    title = input("Enter a title for the printout: ")
    num_wallets_12 = int(input("Enter number of 12-word wallets to generate: "))
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Generate 12-word wallets
    wallets_12_words = []
    for _ in range(num_wallets_12):
        seed_phrase, address, qr_code, derivation_path = generate_seed_phrase_and_address(12)
        wallets_12_words.append((seed_phrase, address, qr_code, derivation_path, now))

    html_content = generate_html_output(title, wallets_12_words)
    
    filename = "12_word_wallets.html"
    with open(filename, "w") as f:
        f.write(html_content)
        
    print(f"Successfully generated wallets in '{filename}'")
    # Provide instruction to open the file
    print(f"To view the wallets, open this file in your browser: file://{os.path.abspath(filename)}")


if __name__ == "__main__":
    # Check if we are in the virtual environment. If not, set it up and rerun.
    if sys.prefix == os.path.abspath(VENV_DIR):
        main_script()
    else:
        setup_virtual_env()
        # Rerun the script within the virtual environment
        python_executable = os.path.join(VENV_DIR, 'bin', 'python')
        os.execv(python_executable, [python_executable] + sys.argv)