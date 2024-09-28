import os
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

def getText():
    rel_path = "../input.pdf"
    script_dir = os.path.dirname(__file__)
    PDF_PATH = os.path.join(script_dir, rel_path)
    reader = PdfReader(PDF_PATH)
    text = reader.pages[0].extract_text()
    return text
    