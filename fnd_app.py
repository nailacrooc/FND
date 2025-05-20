from flask import Flask, render_template, request
from BRIDGE import run_pipeline  # Uses run_pipeline from BRIDGE

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    # Get and sanitize user input
    headline = request.form.get("headline", "").strip()
    content = request.form.get("content", "").strip()

    # Validate input
    if not headline or not content:
        return render_template("index.html", error="Please enter both headline and content.")

    # Run the full categorization + fake news detection pipeline
    category, cat_confidence, label, label_confidence = run_pipeline(headline, content)

    # Format outputs
    category_conf_pct = f"{cat_confidence * 100:.2f}%"
    fake_conf_pct = f"{label_confidence * 100:.2f}%"
    label_str = label

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
