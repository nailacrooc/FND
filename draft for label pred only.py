import pandas as pd
from sklearn.metrics import classification_report
from categorizer import predict_from_headline_content
from FND_politics import predict_politics_label
from FND_health import predict_health_label
from FND_entertainment import predict_entertainment_label
from FND_others import predict_others_label


def run_pipeline(headline, content):
    category_result = predict_from_headline_content([headline], [content])[0]
    category = category_result['predicted_category']
    cat_confidence = category_result['confidence_score']

    if category == "politics":
        label, confidence = predict_politics_label(headline, content)
    elif category == "health":
        label, confidence = predict_health_label(headline, content)
    elif category == "entertainment":
        label, confidence = predict_entertainment_label(headline, content)
    else:
        label, confidence = predict_others_label(headline, content)

    return category, cat_confidence, label, confidence


def evaluate_csv():
    input_csv_path = "C:/Users/johnj/ScrapyTest/ScrapyTest/FND-LATEST/FND/TEST SET for bridge 2.csv"
    output_csv_path = "C:/Users/johnj/ScrapyTest/ScrapyTest/FND-LATEST/FND/TEST SET for bridge 2-output.csv"

    df = pd.read_csv(input_csv_path, encoding='ISO-8859-1')

    success = []
    predictions = {
        "predicted_category": [],
        "category_confidence": [],
        "predicted_label": [],
        "label_confidence": [],
    }

    true_labels = []
    predicted_labels = []

    for _, row in df.iterrows():
        headline = row['Headline']
        content = row['Content'] if 'Content' in df.columns else ""
        true_category = row['Category']
        true_label = row['Label']

        pred_category, cat_conf, pred_label, label_conf = run_pipeline(headline, content)

        predictions["predicted_category"].append(pred_category)
        predictions["category_confidence"].append(cat_conf)
        predictions["predicted_label"].append(pred_label)
        predictions["label_confidence"].append(label_conf)

        # ✅ Success based only on label prediction
        is_success = (true_label == pred_label)
        success.append(is_success)

        true_labels.append(true_label)
        predicted_labels.append(pred_label)

    for col in predictions:
        df[col] = predictions[col]
    df["success"] = success

    df.to_csv(output_csv_path, index=False)
    print(f"\n✅ Results saved to: {output_csv_path}")

    success_rate = sum(success) / len(success)
    print(f"\n📊 Label Accuracy: {success_rate * 100:.2f}% ({sum(success)} / {len(success)})")

    print("\n📋 Classification Report (Labels):")
    print(classification_report(true_labels, predicted_labels, digits=4))


if __name__ == "__main__":
    evaluate_csv()
