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
from scipy.special import expit

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
train_df = pd.read_csv("C:/Users/johnj/ScrapyTest/ScrapyTest/FND-MAY1/FND/ALL_shuffled_na.csv")
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

# ---- Predict Function for CSV with ONLY "Content" Column ----
def predict_from_content_csv(input_csv_path, output_csv_path):
    df = pd.read_csv(input_csv_path, encoding='ISO-8859-1')

    # Take only the first column and rename it to 'Content'
    df = df.iloc[:, [0]].copy()
    df.columns = ['Content']

    # Preprocess
    df['Content'] = df['Content'].astype(str).apply(preprocess_text)

    # Extract features
    sentiment_features = df['Content'].apply(lambda x: pd.Series(extract_sentiment(x)))
    sentiment_sparse = csr_matrix(sentiment_features.values)
    X_tfidf_new = vectorizer.transform(df['Content'])
    X_combined_new = hstack([X_tfidf_new, sentiment_sparse])
    X_svd_new = svd.transform(X_combined_new)
    X_lda_new = lda.transform(X_svd_new)

    # Predict
    y_pred_new = model.predict(X_lda_new)
    confidence_scores = model.predict_proba(X_lda_new)
    
    # Calculate the confidence score for each prediction (highest confidence)
    max_confidence = np.max(confidence_scores, axis=1)

    # Add predictions and confidence scores to the dataframe
    df['predicted_category'] = label_encoder.inverse_transform(y_pred_new)
    df['confidence_score'] = max_confidence

    # Save output
    df.to_csv(output_csv_path, index=False)
    print(f"\nPredictions and confidence scores saved to: {output_csv_path}")

# ---- Example Run ----
predict_from_content_csv(
    input_csv_path="C:/Users/johnj/ScrapyTest/ScrapyTest/FND-MAY1/FND/Test-Random-News.csv",
    output_csv_path="C:/Users/johnj/ScrapyTest/ScrapyTest/FND-MAY1/FND/Test-Random-News-output.csv"
)
