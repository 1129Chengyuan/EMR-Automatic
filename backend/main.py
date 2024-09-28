from flask import Flask, request, jsonify
from flask_cors import CORS

from pymongo import MongoClient
from urllib.parse import quote_plus

from time import time

app = Flask(__name__)
CORS(app)

username = quote_plus('dave')
password = quote_plus('passwordfordb')
uri = f"mongodb+srv://{username}:{password}@cluster0.mwh6h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['UserData']
collection = db['UserCredentials']

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
\
if __name__ == "__main__":
    app.run()
