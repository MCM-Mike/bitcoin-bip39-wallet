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
# YLCN: I added Bip49Coins and Bip84Coins enum imports
from bip_utils import Bip39SeedGenerator, Bip44, Bip49, Bip84, Bip44Coins, Bip44Changes, Bip49Coins, Bip84Coins
from datetime import datetime
import qrcode
import base64
from io import BytesIO
from fpdf import FPDF

def get_user_input():
    strength_choice = input("Choose mnemonic length (12 or 24 words): ").strip()
    strength = 128 if strength_choice == "12" else 256
    seed_name = input("Enter a name for the seed (optional): ").strip()
    return strength, seed_name

def generate_mnemonic(strength):
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=strength)


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
    # YLCN: This returns img object instead of base64 text encoded formaat
    return img

def formatted_now(dt):    
    return dt.utcnow().strftime("%d.%m.%Y %H:%M UTC")
    
   
def get_seed_bytes(mnemonic):
    return Bip39SeedGenerator(mnemonic).Generate()


def derive_root_keys(seed_bytes):    
    """
        This functions derives root keys and returns as dictionary
    """
    
    bip_descriptions = {
            'BIP44': 'Legacy',
            'BIP49': 'Segwit Compatible',
            'BIP84': 'Segwit Native'
        }        
    
    # YLCN: This dictionary is used in the for loop for appropriate constant
    bip_coins = {
        'BIP44': Bip44Coins.BITCOIN,
        'BIP49': Bip49Coins.BITCOIN, 
        'BIP84': Bip84Coins.BITCOIN
     } 
    root_keys = {}
    for bip_type, bip_cls in [('BIP44', Bip44), ('BIP49', Bip49), ('BIP84', Bip84)]:
            # YLCN second parameter used in FromSeed function below was BIP44Coins.BITCOIN
            # for all bip types, I changed it so that appropriate format is used for each type
            bip_obj = bip_cls.FromSeed(seed_bytes, bip_coins[bip_type])
            root_key = bip_obj.PrivateKey().ToExtended()
            root_keys[bip_type]= {'key':root_key,'description':bip_descriptions[bip_type]}
            
    return root_keys

def derive_extended_pub_keys(seed_bytes):
    """
        This functions derives extended pub keys and returns as dictionary
    """
    
    # YLCN: This dictionary is used in the for loop for appropriate constant

    bip_coins = {
        'BIP44': Bip44Coins.BITCOIN,
        'BIP49': Bip49Coins.BITCOIN, 
        'BIP84': Bip84Coins.BITCOIN
    } 
    pub_keys = {}
    for bip_type, bip_cls in [('BIP44', Bip44), ('BIP49', Bip49), ('BIP84', Bip84)]:
        # YLCN second parameter used in FromSeed function below was BIP44Coins.BITCOIN
        # for all bip types, I changed it so that appropriate format is used for each type
        bip_obj = bip_cls.FromSeed(seed_bytes, bip_coins[bip_type])
        account_ext_pub_key = bip_obj.Purpose().Coin().Account(0).PublicKey().ToExtended()
        account_ext_pub_key_qr = generate_qr_code(account_ext_pub_key)
        pub_keys[bip_type] = {'key':account_ext_pub_key,'qr_code':account_ext_pub_key_qr}
    return pub_keys


def derive_derived_addresses(seed_bytes,n_address_count=3):
    """
        This functions creates derived keys and returns as dictionary
    """
    
    # YLCN: This dictionary is used in the for loop for appropriate constant
    bip_coins = {
        'BIP44': Bip44Coins.BITCOIN,
        'BIP49': Bip49Coins.BITCOIN, 
        'BIP84': Bip84Coins.BITCOIN
     } 
    
    derived_addresses = {}
    for bip_type, bip_cls in [('BIP44', Bip44), ('BIP49', Bip49), ('BIP84', Bip84)]:
        # YLCN second parameter used in FromSeed function below was BIP44Coins.BITCOIN
        # for all bip types, I changed it so that appropriate format is used for each type
        bip_obj = bip_cls.FromSeed(seed_bytes, bip_coins[bip_type])
        derived_addresses[bip_type] = []
        for i in range(n_address_count):
            address = bip_obj.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i).PublicKey().ToAddress()
            address_qr_code = generate_qr_code(address)
            derived_addresses[bip_type].append({'address':address,'qr_code':address_qr_code})
    return derived_addresses
    
    
# Helper pdf methods for creating tables

def create_root_keys_table_data(root_keys):
    table_data = []
    # Header
    table_data.append(['BIP Type','Description','Root Key'])
    for bip_type in root_keys:
        root_key = root_keys[bip_type]
        table_data.append([bip_type, root_key['description'], root_key['key']])
    
    return table_data


def create_xpub_keys_table_data(xpub_keys):
    table_data = []
    table_data.append(['BIP Type','Account Extended Public Key','QR Code'])
    for bip_type in xpub_keys:
        table_data.append([bip_type,
                          xpub_keys[bip_type]['key'],
                          xpub_keys[bip_type]['qr_code'].get_image()
                          ])
    return table_data    
    
    
    
def create_derived_addresses_table_data(derived_addresses):
    table_data = {}
    for bip_type in derived_addresses:
        
        table_data[bip_type] = []
        table_data[bip_type].append(['No', 'Address', 'QR Code','Notes'])    
        
        for index,address_data in enumerate(derived_addresses[bip_type]):
            table_data[bip_type].append([
                               str(index+1),
                               address_data['address'],
                               address_data['qr_code'],
                               ''
                               ])
    return table_data



# This class allows to edit footer (and header if needed)
class MyPDF(FPDF):
    
    def header(self):
        # Edit and uncomment below for header 
        # Rendering logo:
        # self.image("../docs/fpdf2-logo.png", 10, 8, 33)
        # Setting font: helvetica bold 15
        # self.set_font("helvetica", "B", 15)
        # Moving cursor to the right:
        # self.cell(80)
        # Printing title:
        # self.cell(30, 10, "Title", border=1, align="C")
        # Performing a line break:
        # self.ln(20)
        pass
    
    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", "I", 8)
        # Printing page number:
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}   {self.seed_name} ({self.now}) ", align="C")
        
 
 
def create_pdf(seed_name, mnemonic):
    # first create raw data 
    seed_bytes = get_seed_bytes(mnemonic)
    root_keys = derive_root_keys(seed_bytes)
    xpub_keys = derive_extended_pub_keys(seed_bytes)
    derived_addresses = derive_derived_addresses(seed_bytes)
    
    # convert data to table format
    root_keys_table_data = create_root_keys_table_data(root_keys)
    xpub_keys_table_data = create_xpub_keys_table_data(xpub_keys)
    derived_addresses_table_data = create_derived_addresses_table_data(derived_addresses)
    
    
    date_time_now = datetime.now()
    now_text = date_time_now.strftime("%d%m%Y_%H%M")
    file_name = f"{seed_name}_{now_text}.pdf" if seed_name else f"{now_text}.pdf"
    
    pdf = MyPDF()
    pdf.seed_name = seed_name # we assign the variables so that it can be used in footer 
    pdf.now = formatted_now(date_time_now) # we assign the variables so that it can be used in footer 
    
    color_1 = (120,120,120)
    
    # First page title-seed name and generated time info
    pdf.add_page()
    pdf.set_font('helvetica',size = 24)
    pdf.cell(txt=f'Seed Information')
    pdf.set_font('helvetica',size=14)
    pdf.ln(12)
    pdf.cell(txt=f'Seed Name: {seed_name}',new_x='LMARGIN',new_y='NEXT')
    pdf.set_font('helvetica','I',size=11)
    pdf.ln(2)
    pdf.cell(txt=f"(generated on {pdf.now})",new_x='LMARGIN',new_y='NEXT')
    pdf.ln(2)
    pdf.set_font('helvetica','B',size=12)

    
    
    #Mnemonic words
    pdf.set_draw_color(color_1)
    pdf.set_line_width(0.5)
    pdf.line(5,pdf.y,pdf.w-5,pdf.y)
    pdf.ln(8)

    pdf.cell(txt='Mnemonic Words:',new_x='LMARGIN',new_y='NEXT')
    MNEMONIC_SECTION_Y = pdf.y
    pdf.ln(1)


    pdf.set_font('helvetica',size=11)
    for i,word in enumerate(mnemonic.split()):
        pdf.cell(txt=f'{i+1:>2}. {word}',new_x='LMARGIN',new_y='NEXT')

    # Place Mneminic qr code image
    mnemonic_qr = generate_qr_code(mnemonic)
    pdf.text(txt='Mnemonic QR Code', x=62,y = MNEMONIC_SECTION_Y)
    pdf.image(mnemonic_qr.get_image(),x=60,y=MNEMONIC_SECTION_Y+3,w=35,h=35)


    pdf.set_draw_color(color_1)
    pdf.set_line_width(0.5)
    pdf.ln(8)
    
    with pdf.table(col_widths=[20,25,130]) as table:
        for data_row in root_keys_table_data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)

            

    pdf.ln(8)
    # We add a new page to start extended public keys from start
    pdf.add_page()
    pdf.set_font('helvetica','B',size=12)
    pdf.cell(txt='Account Extended Public Keys',new_x='LMARGIN',new_y='NEXT')
    pdf.set_font('helvetica',size=11)
    pdf.ln(4)

    with pdf.table(padding=2,col_widths=[20,100,50]) as table:
        for i, data_row in enumerate(xpub_keys_table_data):
            row = table.row()
            for j,datum in enumerate(data_row):
                if j == 2 and i>0:
                    row.cell(img=datum)   
                else:
                    row.cell(datum)     


    pdf.ln(8)    
    pdf.set_font('helvetica','B',size=12)
    pdf.cell(txt='Derived Addresses',new_x='LMARGIN',new_y='NEXT')
    pdf.set_font('helvetica',size=11)
    pdf.ln(8)
    
    for bip_type in derived_addresses_table_data:
        pdf.ln(8)
        pdf.set_font('helvetica','B',size=12)
        pdf.cell(txt=bip_type,new_x='LMARGIN',new_y='NEXT')
        pdf.ln(2)
        with pdf.table(padding=2,col_widths=[10,85,30,30],) as table:
            for i, data_row in enumerate(derived_addresses_table_data[bip_type]):
                row = table.row()
                for j, datum in enumerate(data_row):                   
                    if j == 2 and i>0:
                        row.cell(img=datum.get_image(),img_fill_width=True)
                    else:
                        row.cell(datum,)
            # if no space left in the bottom, add a new page
            pdf.ln(8)
            
            if pdf.h - pdf.y < 30:
                pdf.add_page()           
    
    pdf.output(file_name)
    
    
def main():
    strength,seed_name = get_user_input()
    mnemonic = generate_mnemonic(strength)
    create_pdf(seed_name,mnemonic)

if __name__ == "__main__":
    main()
