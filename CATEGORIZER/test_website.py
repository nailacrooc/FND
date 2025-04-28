import os
from flask import Flask, render_template, request
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import PunktSentenceTokenizer
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
import numpy as np

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

# ---- Load Dataset and Preprocess ----
# Use relative path to the dataset
dataset_path = os.path.join(os.path.dirname(__file__), 'bbc-text3.csv')
dataset = pd.read_csv(dataset_path)

dataset['text'] = dataset['text'].astype(str).apply(preprocess_text)
main_categories = {'politics', 'entertainment', 'health'}
dataset['category'] = dataset['category'].apply(lambda x: x if x in main_categories else 'others')

# ---- TF-IDF Vectorization ----
X = dataset['text']
y = dataset['category']
vectorizer = TfidfVectorizer()
X_tfidf = vectorizer.fit_transform(X)

# ---- Train/Test Split ----
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# ---- Train SVM Model (Updated with probability=True) ----
model = SVC(kernel='linear', probability=True, random_state=42)
model.fit(X_train, y_train)

# ---- Flask Routes ----
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['news_text']
        cleaned_input = preprocess_text(user_input)
        input_vector = vectorizer.transform([cleaned_input])

        # Predict the category probabilities
        probabilities = model.predict_proba(input_vector)[0]
        
        # Get classification report for evaluation
        y_pred = model.predict(X_test)
        eval_metrics = classification_report(y_test, y_pred, target_names=model.classes_, output_dict=True)
        
        # Extract the average probability for each category from the classification report
        category_probabilities = {category: eval_metrics[category]['f1-score'] for category in model.classes_}
        
        # Format the result to show each category and its corresponding probability
        formatted_result = "\n".join([f"{category} {probability:.2f}" for category, probability in category_probabilities.items()])

        return render_template('index.html', result=formatted_result)
    
    return render_template('index.html', result=None)

if __name__ == '__main__':
    app.run(debug=True)
