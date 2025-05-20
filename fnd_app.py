from flask import Flask, render_template, request
from BRIDGE import run_pipeline  # Your pipeline module

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    headline = request.form.get('headline', '').strip()
    content = request.form.get('content', '').strip()

    category, category_conf, label, fake_conf = run_pipeline(headline, content)

    fake_label = "Credible" if label == 1 else "Not Credible"

    return render_template(
        "index.html",
        headline=headline,
        content=content,
        category_pred=category,
        category_conf=int(round(100 * category_conf)),
        fake_pred=fake_label,
        fake_conf=int(round(100 * fake_conf))
    )

if __name__ == "__main__":
    app.run(debug=True)
