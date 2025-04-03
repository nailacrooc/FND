import json
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# Load JSON dataset
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)  # Try loading as a JSON array
        except json.JSONDecodeError:
            f.seek(0)  # Reset file pointer
            return [json.loads(line) for line in f]

# Load dataset
file_path = "C:/Users/johnj/ScrapyTest/ScrapyTest/FND/News_Category_Dataset_v3.json"
data = load_json(file_path)

# Convert to DataFrame
df = pd.DataFrame(data)

# Debug: Print available columns
print("Available columns:", df.columns)

# Ensure required columns exist
if "category" not in df.columns:
    raise ValueError("Dataset must contain a 'category' column.")

if "short_description" not in df.columns:
    raise ValueError("Dataset must contain a 'short_description' column.")

# Group by category
categories = df["category"].unique()

for category in categories:
    # Filter data for this category
    category_df = df[df["category"] == category]
    
    # Preprocess text
    texts = [str(text).lower() for text in category_df["short_description"] if isinstance(text, str)]
    
    if not texts:
        continue  # Skip empty categories

    # Convert text data into a document-term matrix
    vectorizer = CountVectorizer(stop_words='english')
    doc_term_matrix = vectorizer.fit_transform(texts)

    # Print results
    print(f"\nCategory: {category}")
    print("Document-Term Matrix Shape:", doc_term_matrix.shape)
    print("Vocabulary Sample:", list(vectorizer.vocabulary_.items())[:10])
