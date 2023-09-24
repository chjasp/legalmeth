from flask import Flask, request, jsonify, render_template
from google.oauth2 import id_token
from google.auth.transport import requests
from googleapiclient import discovery


from google.auth import default
from google.oauth2 import credentials as oauth2_credentials
from google.oauth2.credentials import Credentials

app = Flask(__name__)

CLIENT_ID = ''
PROJECT_ID = 'steam-378309'
SERVICE_NAME = 'run.services.get'

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/verify', methods=['POST'])
def verify():
    token = request.json['id_token']

    try:
        # Verify the ID token
        print("verify")
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        print(idinfo)

        # Check if the user has the required permissions in project "p123"
        access_granted = check_permissions(idinfo['email'], idinfo)

        return jsonify(access_granted=access_granted)
    except ValueError:
        return jsonify(access_granted=False)

def check_permissions(user_email, idinfo):
    # Check if the user has the "run.invoker" permission on GCP
    credentials, _ = default()
    service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
    policy = service.projects().getIamPolicy(resource=PROJECT_ID, body={}).execute()

    required_role = 'roles/owner'
    member = f'user:{user_email}'

    for binding in policy['bindings']:
        print(binding)
        if binding['role'] == required_role and member in binding['members']:
            return True

    return False

if __name__ == '__main__':
    app.run(debug=True, port=3000)