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

# ---- Load Dataset ----
dataset = pd.read_csv("C:/Users/johnj/ScrapyTest/ScrapyTest/FND-APRIL29/FND/CATEGORIZER/AGA-DINO-LATEST.csv")

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

# ---- User Input Prediction with Confidence Values ----
def predict_category():
    user_input = input("\nEnter a news article: ")
    cleaned_input = preprocess_text(user_input)
    input_vector = vectorizer.transform([cleaned_input])
    
    # Get decision function scores for each class
    decision_scores = model.decision_function(input_vector)
    
    # Apply the sigmoid function to get a confidence score (probability-like score)
    confidence_scores = expit(decision_scores)  # Sigmoid for probabilities
    
    # Get the predicted class
    prediction = model.predict(input_vector)[0]
    
    # Print the predicted category
    print(f"Predicted Category: {prediction}")
    
    # Output the confidence values per category
    print("\nConfidence values per category:")
    for i, category in enumerate(model.classes_):
        print(f"{category}: {confidence_scores[0][i]:.4f}")

# ---- Run ----
predict_category()
