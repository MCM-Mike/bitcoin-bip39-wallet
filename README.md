# Bitcoin Wallet Seed and Key Generator (bip39)

## Overview
This repository, available at [this link](https://github.com/MCM-Mike/bitcoin-bip39-wallet), contains two Python scripts for generating and managing cryptocurrency wallet seeds and keys in compliance with BIP39, BIP44, BIP49, and BIP84 standards. These scripts facilitate the creation of mnemonic phrases, derivation of wallet keys, and generation of QR codes and PDFs for secure and convenient storage of wallet information.

### Scripts
1. **bip39-wallet-gen-QR-codes-markup.py**: Generates mnemonic phrases and derives wallet keys, embedding this information along with QR codes into a text file with markup formatting.
   
2. **bip39-wallet-gen-PDF.py**: Similar to the first script but outputs the wallet information, including QR codes, in a well-formatted PDF document.

## Features
- **Mnemonic Phrase Generation**: Both scripts generate mnemonic phrases of 12 or 24 words.
- **Key Derivation**: Implements BIP39, BIP44, BIP49, and BIP84 standards for key derivation.
- **QR Code Generation**: Creates QR codes for mnemonic phrases, wallet keys, and addresses.
- **Output Formats**:
  - **Markup File**: The first script generates a text file with markup, including QR codes embedded as base64 images.
  - **PDF Document**: The second script creates a PDF document with all relevant wallet information and QR codes.

## Prerequisites
- Python 3.x
- Required Python libraries: `mnemonic`, `bip_utils`, `qrcode`, `base64`, `io`, and `fpdf` for PDF generation.

## Installation

1. Clone the repository:
`git clone https://github.com/MCM-Mike/bitcoin-bip39-wallet`
2. Install the required Python libraries: `pip install mnemonic bip-utils qrcode Pillow base64 fpdf`
   
## Usage
1. Run the desired script: `python bip39-wallet-gen-QR-codes-markup.py`
or `python bip39-wallet-gen-PDF.py`

2. Follow the on-screen prompts to generate your mnemonic phrase and choose the seed name (optional).
3. The output will be saved in the same directory as the script.

## Examples

- **Screenshots**: (Include a couple of screenshots demonstrating the script in action and the output files.)
- **Sample Outputs**: (Provide links to example output files - a markup text file and a PDF document.)

## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your proposed changes.

## License
[Specify the license or insert 'This project is licensed under the [License Name] - see the LICENSE.md file for details']

