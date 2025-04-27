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
dataset = pd.read_csv("C:/Users/johnj/ScrapyTest/ScrapyTest/FND-2/bbc-text3.csv")

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

# ---- Predict Categories from CSV (Hardcoded Path) ----
def predict_from_csv():
    input_path = "C:/Users/johnj/ScrapyTest/ScrapyTest/FND-2/TEST FOR BBC.csv"  # 👈 Your CSV file path here
    try:
        input_df = pd.read_csv(input_path, encoding='ISO-8859-1')  # Or try 'cp1252' if that fails
        if 'text' not in input_df.columns:
            print("The input CSV must contain a 'text' column.")
            return
        input_df['cleaned_text'] = input_df['text'].astype(str).apply(preprocess_text)
        input_vectors = vectorizer.transform(input_df['cleaned_text'])
        predictions = model.predict(input_vectors)
        input_df['predicted_category'] = predictions
        output_path = input_path.replace(".csv", "_with_predictions.csv")
        input_df.to_csv(output_path, index=False)
        print(f"Predictions added. Output saved to: {output_path}")
    except Exception as e:
        print(f"Error: {e}")

# ---- Run ----
predict_from_csv()
