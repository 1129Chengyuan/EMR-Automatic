# Replace with the actual variable/function name
from rag_system_creation import get_metadata_output
import os
# from dotenv import load_dotenv
# from dotenv import load_dotenv
from pypdf import PdfReader
import sys

# Load environment variables
# load_dotenv()

# Add the backend directory to the Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import variables or functions from rag_system_creation.py


def getText():
    rel_path = "../input.pdf"
    script_dir = os.path.dirname(__file__)
    PDF_PATH = os.path.join(script_dir, rel_path)
    reader = PdfReader(PDF_PATH)
    text = reader.pages[0].extract_text()
    text = text.split("\n")
    text = [i for i in text if "General" in i]
    text = text[0]
    text = text[11:]
    return text


def getMetadata(someText):
    # Access a variable from rag_system_creation.py
    # Replace `your_variable_or_function` with the actual name you need
    metadata = get_metadata_output(someText)

    # Return the metadata
    return metadata, metadata[1:]


# # Example usage
# physical_examination_results = getText()  # Extract text from the PDF
# # Get the metadata for the extracted text
# metadata = getMetadata(physical_examination_results)


def main():
    physical_examination_results = getText()  # Extract text from the PDF
    # Get the metadata for the extracted text
    metadata = getMetadata(physical_examination_results)
    return metadata


# Print out the result
# print(metadata)
main()
# print(pdf_text)
