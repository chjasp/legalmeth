from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.get("/")
@app.get("/plan")
def get_index():
    return render_template("plan.html")


@app.get("/research")
def research_get():
    return render_template("research.html")


@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    response = "Response Placeholder"  # get_response(text)
    message = {"answer": response}
    return jsonify(message)


if __name__ == "__main__":
    app.run(debug=True)
