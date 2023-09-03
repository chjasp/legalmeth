import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from backend.db_interface import DatabaseInterface
from backend.query_interface import get_matches

import ssl
print(ssl.OPENSSL_VERSION)

load_dotenv()

app = Flask(__name__) 

PROJECT_ID = os.environ.get("PROJECT_ID")
REGION = os.environ.get("REGION")
INSTANCE_NAME = os.environ.get("INSTANCE_NAME")

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_PORT = os.environ.get("DB_PORT")

INSTANCE_CONNECTION_NAME = f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}"

@app.get("/")
@app.get("/plan")
def get_index():
    return render_template("plan.html")

@app.post("/predict")
def predict():
    query = request.get_json().get("message")
    print(query)
    matches = get_matches(query)
    message = {"matches": matches}
    return jsonify(message)

if __name__ == "__main__":
    app.run(debug=True)
