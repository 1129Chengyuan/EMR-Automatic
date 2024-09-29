from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from pymongo import MongoClient
from urllib.parse import quote_plus

from werkzeug.utils import secure_filename
from bson.binary import Binary
from time import time

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from fpdf import FPDF

import json

from textExtract import main

app = Flask(__name__)
CORS(app)

username = quote_plus('dave')
password = quote_plus('passwordfordb')
uri = f"mongodb+srv://{username}:{password}@cluster0.mwh6h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['UserData']
collection = db['UserCredentials']
collectionP = db['Patients']

@app.route("/")
def suggest_me():
    return "Hello World!"

@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    npi = data.get('npi')
    password = data.get('password')

    exists = collection.find_one({'username': username, 'npi': npi, 'password': password})
    if (exists):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Login failed"}), 400

@app.route("/register", methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    npi = data.get('npi')
    password = data.get('password')

    exists = collection.find_one({'npi': npi})

    if (exists):
        return jsonify({"message": "User already exists"}), 400
    else:
        collection.insert_one({'username': username, 'npi': npi, 'password': password, 'timecreated': time()})
        return jsonify({"message": "User created successfully"}), 201

@app.route("/uploadpdf", methods=['POST'])
def uploadpdf():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    """CHANGE THIS NAME THING TO CALL HIS FUNCTION FOR THE NAME"""
    name = request.form.get('name').lower()
    if (not name):
        return jsonify({"message": "No name provided"}), 400

    name = name.lower()
    # Create a patient if they don't exist
    if collectionP.find_one({'name': name}) is None:
        collectionP.insert_one({'name': name, 'pdfs': []})

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_data = file.read()
        binary_file_data = Binary(file_data)

        # Update patient document with PDF metadata and binary data
        collectionP.update_one(
            {'name': name},
            {'$push': {'pdfs': {'filename': filename, 'upload_date': time(), 'data': binary_file_data}}}
        )
        
        return jsonify({"message": "File uploaded successfully"}), 201
    else:
        return jsonify({"message": "Invalid file type"}), 400

@app.route("/getpdfs", methods=['GET'])
def getpdfs():
    name = request.args.get('name')
    pdfNames = []
    pat = collectionP.find_one({'name': name})
    if pat is not None:
        for pdf in pat['pdfs']:
            pdfNames.append(pdf['filename'])
        return jsonify({"pdfs": pdfNames}), 200
    else:
        return jsonify({"pdfs": pdfNames, "message": "Patient not found"}), 404

def create_printable_string(bodyText):
    # Initialize the printable string
    printable_string = ""

    # Add the first part of the bodyText
    printable_string += bodyText[0] + "\n\n"

    # Convert the JSON string in bodyText[1] to a list of medications
    medications = json.loads(bodyText[1])
    printable_string += "Medications:\n"
    for i, med in enumerate(medications, start=1):
        printable_string += f"{i}. {med['name']} - {med['dose']}\n"

    # Add the third part of the bodyText
    if (len(bodyText) > 2):
        printable_string += "\n" + bodyText[2]

    return printable_string


def create_pdf_from_string(text, output_path):
    # Write the text to a temporary file
    with open("myfile.txt", "w") as f:
        f.write(text)

    # Create an instance of FPDF
    pdf = FPDF()
    
    # Add a page
    pdf.add_page()
    
    # Set style and size of font
    pdf.set_font("Arial", size=15)
    
    # Open the text file in read mode
    with open("myfile.txt", "r") as f:
        # Insert the texts in pdf using multi_cell
        for line in f:
            pdf.multi_cell(0, 10, txt=line, align='L')
    
    # Save the pdf with the specified name
    pdf.output(output_path)

def append_pdfs(input_pdf_path, output_pdf_path, appended_pdf_path):
    pdf_writer = PdfWriter()

    # Read the input PDF
    input_pdf = PdfReader(input_pdf_path)
    for page_num in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_num]
        pdf_writer.add_page(page)

    # Read the appended PDF
    appended_pdf = PdfReader(appended_pdf_path)
    for page_num in range(len(appended_pdf.pages)):
        page = appended_pdf.pages[page_num]
        pdf_writer.add_page(page)

    # Write the combined PDF to the output path
    with open(output_pdf_path, 'wb') as out_pdf:
        pdf_writer.write(out_pdf)

def create_and_append_pdf(text, input_pdf_path, output_pdf_path):
    temp_pdf_path = "temp.pdf"
    create_pdf_from_string(text, temp_pdf_path)
    append_pdfs(input_pdf_path, output_pdf_path, temp_pdf_path)


@app.route("/getpdf", methods=['GET'])
def getpdf():
    
    print("Find pdf")

    name = request.args.get('name')
    pdfName = request.args.get('pdfName')
    patient = collectionP.find_one({'name': name})
    bodyText = "The file was not converted successfully"
    if patient is not None:
        for pdf in patient['pdfs']:
            if pdf['filename'] == pdfName:

                print("Found pdf")

                with open("input.pdf", "wb") as f:
                    f.write(pdf['data'])
                bodyText = main()
                # bodyText = ['Irritable Bowel Syndrome (IBS)\nMedical Information: IBS is a common disorder affecting the large intestine, causing symptoms like cramping, abdominal pain, bloating, gas, and diarrhea or constipation. The exact cause is unknown, but factors like diet, stress, and gut bacteria play a role.\nTreatment Suggestions: Treatment for IBS focuses on relieving symptoms. Dietary changes like increasing fiber intake or following a low FODMAP diet can help. Medications include antispasmodics, laxatives, o...', '[{"name": "Loperamide", "dose": "2mg"}, {"name": "Dicyclomine", "dose": "20mg"}, {"name": "Amitriptyline", "dose": "10mg"}]', 'Monitor vital signs, administer prescribed medications, provide emotional support, assist with hygiene care, encourage fluid intake, document intake and output, assist with mobility exercises, monitor bowel movements, provide dietary guidance.']
                if len(bodyText) >= 2:
                    bodyText = create_printable_string(bodyText)
                elif len(bodyText) == 1:
                    bodyText = bodyText[0]
                break
        create_and_append_pdf(bodyText, "input.pdf", "lib/download.pdf")
        return jsonify({"bodytext": bodyText})
    else:
        return jsonify({"bodytext": "Patient not found"})

# @app.route("/downloadpdf", methods=['GET'])
# def downloadpdf():
#     f = open("lib/download.pdf", "rb")
#     return f.read()

@app.route("/downloadpdf", methods=['GET'])
def downloadpdf():
    return send_file("lib/download.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run()
