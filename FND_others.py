import os
import pickle
import pandas as pd
import numpy as np
from scipy.sparse import hstack
from sklearn.model_selection import train_test_split
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import string
import re

# Download necessary NLTK data
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('vader_lexicon')

TFIDF_FILE = "others_tfidf.pkl"
LDA_FILE = "others_lda.pkl"
SVM_FILE = "others_svm.pkl"

analyzer = SentimentIntensityAnalyzer()

def preprocess_text(text):
    if pd.isnull(text):
        return ""
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [word if word == "us" else lemmatizer.lemmatize(word) for word in tokens]
    return " ".join(tokens)

def train_others_model():
    print("Training new others model...")

    df = pd.read_csv("C:/Users/johnj/ScrapyTest/ScrapyTest/FND-MAY1/FND/OTHERS-cleaned.csv", encoding="ISO-8859-1", on_bad_lines="skip")
    df = df.dropna(subset=['Label'])
    df['combined_text'] = df['Headline'].fillna('') + " " + df['Content'].fillna('')
    df['clean_text'] = df['combined_text'].apply(preprocess_text)

    X = df['clean_text']
    y = df['Label']
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    tfidf = TfidfVectorizer(max_features=5000)
    X_train_tfidf = tfidf.fit_transform(X_train_raw)
    X_test_tfidf = tfidf.transform(X_test_raw)
    with open(TFIDF_FILE, "wb") as f:
        pickle.dump(tfidf, f)

    X_train_sent = np.array(X_train_raw.apply(lambda x: analyzer.polarity_scores(x)['compound'])).reshape(-1, 1)
    X_test_sent = np.array(X_test_raw.apply(lambda x: analyzer.polarity_scores(x)['compound'])).reshape(-1, 1)

    X_train_feats = hstack([X_train_tfidf, X_train_sent])
    X_test_feats = hstack([X_test_tfidf, X_test_sent])

    lda = LinearDiscriminantAnalysis(n_components=1)
    X_train_lda = lda.fit_transform(X_train_feats.toarray(), y_train)
    X_test_lda = lda.transform(X_test_feats.toarray())
    with open(LDA_FILE, "wb") as f:
        pickle.dump(lda, f)

    svm = SVC(kernel='linear', C=0.1, probability=True, random_state=42)
    svm.fit(X_train_lda, y_train)
    with open(SVM_FILE, "wb") as f:
        pickle.dump(svm, f)

    y_pred = svm.predict(X_test_lda)
    print(f"\n[Others] Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("[Others] Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Not Credible', 'Credible']))

def load_others_models():
    if not (os.path.exists(TFIDF_FILE) and os.path.exists(LDA_FILE) and os.path.exists(SVM_FILE)):
        train_others_model()

    with open(TFIDF_FILE, "rb") as f:
        tfidf = pickle.load(f)
    with open(LDA_FILE, "rb") as f:
        lda = pickle.load(f)
    with open(SVM_FILE, "rb") as f:
        svm = pickle.load(f)
    return tfidf, lda, svm

def predict_others_label(headline, content):
    tfidf, lda, svm = load_others_models()
    raw = f"{headline or ''} {content or ''}"
    clean = preprocess_text(raw)
    tfidf_vec = tfidf.transform([clean])
    sentiment = analyzer.polarity_scores(raw)['compound']
    sent_vec = np.array([[sentiment]])
    feats = hstack([tfidf_vec, sent_vec])
    lda_feats = lda.transform(feats.toarray())
    pred = svm.predict(lda_feats)[0]
    conf = np.max(svm.predict_proba(lda_feats))
    return pred, conf
