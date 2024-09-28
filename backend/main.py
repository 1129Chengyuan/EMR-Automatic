from flask import Flask, request, jsonify
from flask_cors import CORS

from pymongo import MongoClient
from urllib.parse import quote_plus

from werkzeug.utils import secure_filename
from bson.binary import Binary
from time import time

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
            print(pdfNames)
        return jsonify({"pdfs": pdfNames}), 200
    else:
        return jsonify({"pdfs": pdfNames, "message": "Patient not found"}), 404

@app.route("/getpdf", methods=['GET'])
def getpdf():
    return "PDF Data"

if __name__ == "__main__":
    app.run()
