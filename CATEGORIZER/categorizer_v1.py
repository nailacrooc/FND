import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, RandomizedSearchCV

print("Starting the script...")

# Load dataset
df = pd.read_json('C:/Users/johnj/ScrapyTest/ScrapyTest/FND/News_Category_Dataset_v3.json', lines=True)
df.columns = df.columns.str.strip()
print("Dataset loaded successfully.")

# Preprocess data
df['text'] = df['headline'] + " " + df['short_description']
df.dropna(subset=['text', 'category'], inplace=True)

# Split data
X = df['text']
y = df['category']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("Data split into training and testing sets.")

# Vectorize text
tfidf = TfidfVectorizer(stop_words='english', max_df=0.95, min_df=2, ngram_range=(1, 2))
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)
print("Text vectorization complete.")

# Train model
print("Training model...")
param_grid = {'C': [0.1, 1, 10]}
random_search = RandomizedSearchCV(LinearSVC(), param_grid, cv=3, n_iter=3, random_state=42)
random_search.fit(X_train_tfidf, y_train)
model = random_search.best_estimator_
print("Model training complete.")

# Evaluate model
y_pred = model.predict(X_test_tfidf)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

print("Script execution finished.")