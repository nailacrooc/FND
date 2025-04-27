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

# ---- Custom Tokenizer Setup ----
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
dataset = pd.read_csv("C:/Users/johnj/ScrapyTest/ScrapyTest/FND-1/bbc-text.csv")
dataset['text'] = dataset['text'].astype(str).apply(preprocess_text)

# ---- Keep only relevant categories ----
main_categories = {'politics', 'entertainment'}
dataset['category'] = dataset['category'].apply(lambda x: x if x in main_categories else 'others')

# ---- TF-IDF Vectorization ----
X = dataset['text']
y = dataset['category']
vectorizer = TfidfVectorizer()
X_tfidf = vectorizer.fit_transform(X)

# ---- Train/Test Split ----
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# ---- Train SVM Model with Probability ----
model = SVC(kernel='linear', probability=True, random_state=42)
model.fit(X_train, y_train)

# ---- Evaluate ----
y_pred = model.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=model.classes_))

# ---- Predict categories for the entire CSV ----
def categorize_all_rows(input_csv, output_csv):
    # Load and preprocess input CSV
    df = pd.read_csv(input_csv)
    df['Content'] = df['Content'].astype(str).apply(preprocess_text)
    
    # Transform using existing vectorizer
    X_all = vectorizer.transform(df['Content'])
    
    # Predict probabilities
    probs = model.predict_proba(X_all)
    predictions = []
    
    for i, row in enumerate(probs):
        pred_index = row.argmax()
        pred_label = model.classes_[pred_index]
        confidence = row[pred_index]
        # Apply confidence threshold
        if confidence < 0.9:
            predictions.append("others")
        else:
            predictions.append(pred_label)
    
    df['predicted_category'] = predictions
    df.to_csv(output_csv, index=False)
    print(f"\n✅ Categorized file saved to: {output_csv}")

# ---- Run Categorization on Entire CSV ----
categorize_all_rows(
    input_csv="C:/Users/johnj/ScrapyTest/ScrapyTest/FND-1/EmpireNewsNet.csv",
    output_csv="C:/Users/johnj/ScrapyTest/ScrapyTest/FND-1/categorized_output.csv"
)
