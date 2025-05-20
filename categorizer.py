import os
import pickle
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from scipy.sparse import hstack, csr_matrix

# ---- Download NLTK Resources ----
nltk.download('stopwords')
nltk.download('vader_lexicon')

# ---- Global Setup ----
stop_words = set(stopwords.words('english'))
sia = SentimentIntensityAnalyzer()

def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    return ' '.join([word for word in tokens if word not in stop_words])

def extract_sentiment(text):
    scores = sia.polarity_scores(text)
    return [scores['neg'], scores['neu'], scores['pos'], scores['compound']]

def train_and_save_models(csv_path, model_dir):
    print("Training category prediction model...")

    # Load and preprocess data
    df = pd.read_csv(csv_path)
    df = df.sample(frac=1, random_state=42)  # shuffle
    df['Content'] = df['Content'].astype(str).apply(preprocess_text)
    df['Category'] = df['Category'].apply(lambda x: x if x in ['politics', 'entertainment', 'health'] else 'others')

    # TF-IDF and Sentiment
    sentiment_features = df['Content'].apply(lambda x: pd.Series(extract_sentiment(x)))
    sentiment_sparse = csr_matrix(sentiment_features.values)
    vectorizer = TfidfVectorizer(max_features=10000)
    X_tfidf = vectorizer.fit_transform(df['Content'])
    X_combined = hstack([X_tfidf, sentiment_sparse])

    # Encode labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df['Category'])

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_combined, y, test_size=0.2, random_state=42)

    # SVD and LDA
    svd = TruncatedSVD(n_components=200, random_state=42)
    X_train_svd = svd.fit_transform(X_train)
    X_test_svd = svd.transform(X_test)

    lda = LinearDiscriminantAnalysis()
    X_train_lda = lda.fit_transform(X_train_svd, y_train)
    X_test_lda = lda.transform(X_test_svd)

    # Train SVM
    model = SVC(kernel='linear', probability=True, random_state=42)
    model.fit(X_train_lda, y_train)

    # Evaluate
    y_pred = model.predict(X_test_lda)
    print("\n[Category Classification Report]")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

    # Save model components
    with open(os.path.join(model_dir, "vectorizer.pkl"), "wb") as f: pickle.dump(vectorizer, f)
    with open(os.path.join(model_dir, "svd.pkl"), "wb") as f: pickle.dump(svd, f)
    with open(os.path.join(model_dir, "lda.pkl"), "wb") as f: pickle.dump(lda, f)
    with open(os.path.join(model_dir, "svm_model.pkl"), "wb") as f: pickle.dump(model, f)
    with open(os.path.join(model_dir, "label_encoder.pkl"), "wb") as f: pickle.dump(label_encoder, f)

    print("Category model training complete. All files saved.")

def load_models(model_dir):
    with open(os.path.join(model_dir, "vectorizer.pkl"), "rb") as f: vectorizer = pickle.load(f)
    with open(os.path.join(model_dir, "svd.pkl"), "rb") as f: svd = pickle.load(f)
    with open(os.path.join(model_dir, "lda.pkl"), "rb") as f: lda = pickle.load(f)
    with open(os.path.join(model_dir, "svm_model.pkl"), "rb") as f: model = pickle.load(f)
    with open(os.path.join(model_dir, "label_encoder.pkl"), "rb") as f: label_encoder = pickle.load(f)
    return vectorizer, svd, lda, model, label_encoder

# ---- Predict Category Function ----
def predict_category(headline, content):
    user_text = f"{headline} {content}"  # combine both
    model_dir = "category_model"
    os.makedirs(model_dir, exist_ok=True)
    csv_path = "C:/Users/johnj/ScrapyTest/ScrapyTest/FND-MAY1/FND/shuffled_AGA-DINO-LATEST.csv"

    # Train model if not present
    required_files = ["vectorizer.pkl", "svd.pkl", "lda.pkl", "svm_model.pkl", "label_encoder.pkl"]
    if not all(os.path.exists(os.path.join(model_dir, file)) for file in required_files):
        train_and_save_models(csv_path, model_dir)

    # Load models
    vectorizer, svd, lda, model, label_encoder = load_models(model_dir)

    # Preprocess
    processed = preprocess_text(user_text)
    sentiment = pd.Series(extract_sentiment(processed)).values.reshape(1, -1)
    sentiment_sparse = csr_matrix(sentiment)
    X_tfidf = vectorizer.transform([processed])
    X_combined = hstack([X_tfidf, sentiment_sparse])
    X_svd = svd.transform(X_combined)
    X_lda = lda.transform(X_svd)

    # Predict category
    y_pred = model.predict(X_lda)
    y_proba = model.predict_proba(X_lda)
    confidence = np.max(y_proba)
    predicted_category = label_encoder.inverse_transform(y_pred)[0]

    print(f"\n[Category Prediction] → {predicted_category} (Confidence: {confidence:.4f})")
    return predicted_category, float(confidence)
