import os
import joblib
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import PunktSentenceTokenizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report

# --- NLTK Downloads (run once) ---
nltk.download('punkt')
nltk.download('stopwords')

# --- Preprocessing ---
stop_words = set(stopwords.words('english'))
tokenizer = PunktSentenceTokenizer()

def preprocess_text(text):
    if pd.isnull(text) or not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = tokenizer.tokenize(text)
    filtered = [word for word in tokens if word not in stop_words]
    return ' '.join(filtered)

# --- Paths ---
MODEL_DIR = "models/categorizer"
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

# --- Load dataset ---
dataset = pd.read_csv("C:/Users/johnj/ScrapyTest/ScrapyTest/FND-MAY1/FND/shuffled_AGA-DINO-LATEST.csv")
dataset['Content'] = dataset['Content'].astype(str)
dataset['Combined'] = dataset['Content'].apply(preprocess_text)
dataset['Category'] = dataset['Category'].apply(lambda x: x if x in {'politics', 'entertainment', 'health'} else 'others')

# --- Train/test split ---
X = dataset['Combined']
y = dataset['Category']
X_train_text, X_test_text, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Train or Load Model ---
if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
    print("Training categorizer...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    vectorizer = TfidfVectorizer()
    X_train = vectorizer.fit_transform(X_train_text)
    X_test = vectorizer.transform(X_test_text)

    model = SVC(kernel='linear', probability=True)
    model.fit(X_train, y_train)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print("Model and vectorizer saved!")
else:
    print("Loading existing categorizer...")
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    X_train = vectorizer.transform(X_train_text)
    X_test = vectorizer.transform(X_test_text)

# --- Classification Report on Load ---
y_pred = model.predict(X_test)
print("\n--- Full Test Set Classification Report ---")
print(classification_report(y_test, y_pred, zero_division=0))

# --- Prediction Function ---
def predict_category(headline: str, content: str) -> tuple:
    """
    Predict category based on combined headline + content input.
    
    Returns:
      predicted_label (str): predicted category label
      confidence (float): probability/confidence score of prediction
    """
    combined_text = (headline or "") + " " + (content or "")
    cleaned = preprocess_text(combined_text)
    input_vector = vectorizer.transform([cleaned])
    proba = model.predict_proba(input_vector)[0]
    predicted_class_index = proba.argmax()
    predicted_label = model.classes_[predicted_class_index]
    confidence = proba[predicted_class_index]

    print(f"\nPredicted Category: {predicted_label}")
    print(f"Confidence Score:   {confidence:.4f}")
    return predicted_label, confidence
