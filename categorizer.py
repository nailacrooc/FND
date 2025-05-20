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

# ---- Setup ----
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

# ---- Load and Prepare Training Data ----
train_df = pd.read_csv("C:/Users/johnj/ScrapyTest/ScrapyTest/FND-LATEST/FND/CATEGORIZER-DATASETS_shuffled.csv", encoding="ISO-8859-1", on_bad_lines="skip")
train_df = train_df.sample(frac=1, random_state=42)
train_df['Content'] = train_df['Content'].astype(str).apply(preprocess_text)
train_df['Category'] = train_df['Category'].apply(lambda x: x if x in ['politics', 'entertainment', 'health'] else 'others')

# Sentiment + TF-IDF
sentiment_features = train_df['Content'].apply(lambda x: pd.Series(extract_sentiment(x)))
sentiment_sparse = csr_matrix(sentiment_features.values)
vectorizer = TfidfVectorizer(max_features=10000)
X_tfidf = vectorizer.fit_transform(train_df['Content'])
X_combined = hstack([X_tfidf, sentiment_sparse])

# Encode labels
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(train_df['Category'])

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X_combined, y, test_size=0.2, random_state=42)

# Dimensionality Reduction
svd = TruncatedSVD(n_components=200, random_state=42)
X_train_svd = svd.fit_transform(X_train)
X_test_svd = svd.transform(X_test)

lda = LinearDiscriminantAnalysis()
X_train_lda = lda.fit_transform(X_train_svd, y_train)
X_test_lda = lda.transform(X_test_svd)

# Train SVM
model = SVC(kernel='linear', random_state=42, probability=True)
model.fit(X_train_lda, y_train)

# Evaluation
y_pred = model.predict(X_test_lda)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))


# ---- Prediction function supporting headline + content inputs ----
def predict_from_headline_content(headlines, contents):

    # Support single string input for headline or content
    if isinstance(headlines, str):
        headlines = [headlines]
    if isinstance(contents, str):
        contents = [contents]

    # Combine headline and content into one string per example
    combined_texts = [f"{h} {c}" for h, c in zip(headlines, contents)]

    # Preprocess combined texts
    processed_texts = [preprocess_text(t) for t in combined_texts]

    # Extract sentiment features
    sentiment_features = [extract_sentiment(t) for t in processed_texts]
    sentiment_sparse = csr_matrix(sentiment_features)

    # TF-IDF vectorization
    X_tfidf_new = vectorizer.transform(processed_texts)

    # Combine features
    X_combined_new = hstack([X_tfidf_new, sentiment_sparse])

    # Dimensionality reduction
    X_svd_new = svd.transform(X_combined_new)
    X_lda_new = lda.transform(X_svd_new)

    # Prediction
    y_pred_new = model.predict(X_lda_new)
    confidence_scores = model.predict_proba(X_lda_new)
    max_confidence = np.max(confidence_scores, axis=1)

    # Decode labels and pair with confidence
    results = []
    for pred, conf in zip(label_encoder.inverse_transform(y_pred_new), max_confidence):
        results.append({'predicted_category': pred, 'confidence_score': conf})

    return results
