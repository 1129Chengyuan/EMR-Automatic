import os
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

rel_path = "../input.pdf"
script_dir = os.path.dirname(__file__)
PDF_PATH = os.path.join(script_dir, rel_path)
def getText(path):
    reader = PdfReader(path)
    text = reader.pages[0].extract_text()
    return text
    
print(getText(PDF_PATH))