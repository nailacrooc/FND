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
from sklearn.preprocessing import LabelEncoder
from scipy.sparse import hstack, csr_matrix

# ---- Download NLTK Resources ----
nltk.download('stopwords')
nltk.download('vader_lexicon')

# ---- Setup ----
stop_words = set(stopwords.words('english'))
sia = SentimentIntensityAnalyzer()
PICKLE_PATH = "category_model.pkl"

# ---- Text Preprocessing ----
def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    return ' '.join([w for w in tokens if w not in stop_words])

# ---- Sentiment Feature Extraction ----
def extract_sentiment(text):
    scores = sia.polarity_scores(text)
    return [scores['neg'], scores['neu'], scores['pos'], scores['compound']]

# ---- Train and Save Model (if not exists) ----
if not os.path.exists(PICKLE_PATH):
    print("Training model...")

    # Load and prepare data
    df = pd.read_csv(
        "C:/Users/johnj/ScrapyTest/ScrapyTest/FND-LATEST/FND/CATEGORIZER-DATASETS_shuffled.csv",
        usecols=['Content','Headline','Category'],
        encoding="ISO-8859-1",
        on_bad_lines="skip"
    )
    df = df.sample(frac=1, random_state=42)
    
    df['Content']  = df['Content'].astype(str).apply(preprocess_text)
    df['Headline'] = df['Headline'].astype(str).apply(preprocess_text)
    
    df['Category'] = df['Category'].apply(
        lambda x: x if x in ['politics', 'entertainment', 'health'] else 'others'
    )
    
    sent_feat = df['Content'].apply(lambda x: pd.Series(extract_sentiment(x)))
    sent_sparse = csr_matrix(sent_feat.values)
    
    vect_content = TfidfVectorizer(max_features=8000)
    Xc = vect_content.fit_transform(df['Content'])
    
    vect_head = TfidfVectorizer(max_features=2000)
    Xh = vect_head.fit_transform(df['Headline'])
    
    X = hstack([Xc, Xh, sent_sparse])
    
    le = LabelEncoder()
    y = le.fit_transform(df['Category'])
    
    svd = TruncatedSVD(n_components=200, random_state=42)
    X_svd = svd.fit_transform(X)
    
    lda = LinearDiscriminantAnalysis()
    X_lda = lda.fit_transform(X_svd, y)
    
    model = SVC(kernel='linear', probability=True, random_state=42)
    model.fit(X_lda, y)
    
    # Save all components
    with open(PICKLE_PATH, 'wb') as f:
        pickle.dump({
            'model': model,
            'vectorizer_content': vect_content,
            'vectorizer_headline': vect_head,
            'svd': svd,
            'lda': lda,
            'label_encoder': le
        }, f)
    
    print("Model trained and saved.")
else:
    print("Model loaded from pickle.")

# ---- Predict Function from Headline & Content ----
def predict_category(headline, content):
    with open(PICKLE_PATH, 'rb') as f:
        saved = pickle.load(f)
    
    model = saved['model']
    vect_content = saved['vectorizer_content']
    vect_headline = saved['vectorizer_headline']
    svd = saved['svd']
    lda = saved['lda']
    le = saved['label_encoder']
    
    # Preprocess
    headline = preprocess_text(headline)
    content = preprocess_text(content)
    
    sent_vector = csr_matrix([extract_sentiment(content)])
    Xc = vect_content.transform([content])
    Xh = vect_headline.transform([headline])
    X_combined = hstack([Xc, Xh, sent_vector])
    
    X_svd = svd.transform(X_combined)
    X_lda = lda.transform(X_svd)
    
    pred = model.predict(X_lda)[0]
    prob = np.max(model.predict_proba(X_lda))
    
    category = le.inverse_transform([pred])[0]
    return category, float(prob)
