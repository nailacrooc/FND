from flask import Flask, render_template, request
from BRIDGE import run_pipeline  # replace with your module name

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    headline = request.form.get("headline", "").strip()
    content = request.form.get("content", "").strip()

    if not headline or not content:
        return render_template("index.html", error="Please enter both headline and content.")

    category, cat_confidence, label, label_confidence = run_pipeline(headline, content)

    # Convert confidences to percentage string rounded to 2 decimals
    category_conf_pct = f"{cat_confidence * 100:.2f}"
    fake_conf_pct = f"{label_confidence * 100:.2f}"

    # Convert label to string
    label_str = "Credible" if label == 1 else "Not Credible"

    return render_template(
        "index.html",
        headline=headline,
        content=content,
        category_pred=category,
        category_conf=category_conf_pct,
        fake_pred=label_str,
        fake_conf=fake_conf_pct,
    )

if __name__ == "__main__":
    app.run(debug=True)
