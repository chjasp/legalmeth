import os
import openai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from backend.db_interface import DatabaseInterface
from backend.query_interface import get_matches
from backend.prompt_templates import load_hlp_prompt

import ssl
print(ssl.OPENSSL_VERSION)

load_dotenv()

app = Flask(__name__) 

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

print(OPENAI_API_KEY)

PROJECT_ID = os.environ.get("PROJECT_ID")
REGION = os.environ.get("REGION")
INSTANCE_NAME = os.environ.get("INSTANCE_NAME")

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_PORT = os.environ.get("DB_PORT")

INSTANCE_CONNECTION_NAME = f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}"

def generate_prompt(query, matches):
    prompt_template = load_hlp_prompt()
    snippets = "\n".join([f"{i+1}. {match}" for i, match in enumerate(matches)])
    prompt = prompt_template.format(question=query, snippets=snippets)
    return prompt

def call_openai_api(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
        max_tokens=300,
        n=1,
        stop=None,
        temperature=0.7,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

@app.get("/")
@app.get("/plan")
def get_index():
    return render_template("plan.html")

@app.post("/predict")
def predict():
    query = request.get_json().get("message")
    print(query)
    matches = get_matches(query)
    print(matches)
    matches_text = [match["caption"] for match in matches]
    prompt = generate_prompt(query, matches_text)
    answer = call_openai_api(prompt)
    message = {"matches": matches_text, "answer": answer}
    return jsonify(message)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
