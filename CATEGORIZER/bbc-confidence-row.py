import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import PunktSentenceTokenizer
from nltk.sentiment import SentimentIntensityAnalyzer
import numpy as np
from scipy.special import expit  # For sigmoid function

from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report

# ---- Properly Download NLTK Resources ----
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')

# ---- NLTK Setup ----
stop_words = set(stopwords.words('english'))
sia = SentimentIntensityAnalyzer()
tokenizer = PunktSentenceTokenizer()

# ---- Preprocessing Function ----
def preprocess_text(text):
    if pd.isnull(text):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = tokenizer.tokenize(text)
    filtered = [word for word in tokens if word not in stop_words]
    return ' '.join(filtered)

# ---- Load Training Dataset ----
dataset = pd.read_csv("C:/Users/johnj/ScrapyTest/ScrapyTest/FND-APRIL30/FND/CATEGORIZER/news-article-categories.csv")

# ---- Preprocess Text ----
dataset['text'] = dataset['text'].astype(str).apply(preprocess_text)

# ---- Keep only relevant categories ----
main_categories = {'politics', 'entertainment', 'health'}
dataset['category'] = dataset['category'].apply(lambda x: x if x in main_categories else 'others')

# ---- TF-IDF Vectorization ----
X = dataset['text']
y = dataset['category']
vectorizer = TfidfVectorizer()
X_tfidf = vectorizer.fit_transform(X)

# ---- Train/Test Split ----
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# ---- Train SVM Model ----
model = SVC(kernel='linear', random_state=42)
model.fit(X_train, y_train)

# ---- Evaluate Model ----
y_pred = model.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=model.classes_))

# ---- Confidence Threshold for "others" Category ----
OTHERS_CONFIDENCE_THRESHOLD = 0.6  # You can tune this value

# ---- Predict Categories with Confidence for a New CSV File ----
def categorize_csv_file(input_csv_path, output_csv_path, threshold=OTHERS_CONFIDENCE_THRESHOLD):
    # Load the new CSV file with fallback encoding
    new_data = pd.read_csv(input_csv_path, encoding='ISO-8859-1')

    # Check if 'text' column exists
    if 'text' not in new_data.columns:
        raise ValueError("The input CSV must contain a 'text' column.")

    # Preprocess the text column
    new_data['text'] = new_data['text'].astype(str).apply(preprocess_text)

    # Transform using the trained TF-IDF vectorizer
    new_tfidf = vectorizer.transform(new_data['text'])

    # Get decision function scores for each class
    decision_scores = model.decision_function(new_tfidf)

    # Apply the sigmoid function to get confidence scores (probability-like scores)
    confidence_scores = expit(decision_scores)  # Sigmoid for probabilities

    # Create columns for confidence scores per category
    for i, category in enumerate(model.classes_):
        new_data[f'confidence_{category}'] = confidence_scores[:, i]

    # Predict categories with confidence threshold for "others"
    predicted_categories = []
    for i in range(confidence_scores.shape[0]):
        row_conf = confidence_scores[i]
        max_conf_idx = np.argmax(row_conf)
        max_conf = row_conf[max_conf_idx]
        if max_conf < threshold:
            predicted_categories.append("others")
        else:
            predicted_categories.append(model.classes_[max_conf_idx])

    new_data['predicted_category'] = predicted_categories

    # Save to a new CSV file
    new_data.to_csv(output_csv_path, index=False)
    print(f"\nPredicted categories with confidence values saved to: {output_csv_path}")

# ---- Run Categorization on New File ----
# CHANGE THESE PATHS TO MATCH YOUR FILE LOCATIONS
categorize_csv_file(
    input_csv_path="C:/Users/johnj/ScrapyTest/ScrapyTest/FND-APRIL30/FND/CATEGORIZER/TEST-mga-others.csv",
    output_csv_path="C:/Users/johnj/ScrapyTest/ScrapyTest/FND-APRIL30/FND/CATEGORIZER/TEST-mga-others-confidence.csv"
)
