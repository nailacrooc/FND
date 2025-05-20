from categorizer import predict_from_headline_content
from FND_politics import predict_politics_label
from FND_health import predict_health_label
from FND_entertainment import predict_entertainment_label
from FND_others import predict_others_label


def run_pipeline(headline, content):
    print("\n--- Pipeline Start ---")
    print(f"Input Headline: {headline}")
    print(f"Input Content:  {content}\n")

    # Step 1: Predict category
    category_result = predict_from_headline_content([headline], [content])[0]
    category = category_result['predicted_category']
    cat_confidence = category_result['confidence_score']

    print(f"[Category Prediction] Predicted Category: {category} (Confidence: {cat_confidence:.4f})")

    # Step 2: Predict fake news label based on predicted category
    # Pass headline and content as separate args to specialized model
    if category == "politics":
        label, confidence = predict_politics_label(headline, content)
    elif category == "health":
        label, confidence = predict_health_label(headline, content)
    elif category == "entertainment":
        label, confidence = predict_entertainment_label(headline, content)
    else:
        label, confidence = predict_others_label(headline, content)

    label_str = label
    print(f"[Fake News Detection] Label: {label_str} | Confidence: {confidence:.4f}")
    print("--- FND Pipeline End ---\n")

    return category, cat_confidence, label, confidence


if __name__ == "__main__":
    print("Please enter the news headline:")
    user_headline = input().strip()
    print("Please enter the news content:")
    user_content = input().strip()

    run_pipeline(user_headline, user_content)
