from flask import Flask

from flask import request, jsonify

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/login", methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    print("Username: ", username, "Password: ", password)
    return "Login"

@app.route("/register")
def register():
    return "Register"

if __name__ == "__main__":
    app.run()