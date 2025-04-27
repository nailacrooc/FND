import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import TreebankWordTokenizer
from nltk.stem import WordNetLemmatizer

# ---- Download NLTK Resources ----
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# ---- Setup ----
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
tokenizer = TreebankWordTokenizer()

# ---- Preprocessing Function ----
def preprocess_text(text):
    if pd.isnull(text):
        return ""

    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = tokenizer.tokenize(text)

    cleaned = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words
    ]

    return ' '.join(cleaned)

# ---- Load Dataset ----
input_file = "C:/Users/johnj/ScrapyTest/ScrapyTest/FND-1/news-article-categories.csv"
df = pd.read_csv(input_file)

# ---- Clean Text Column ----
df['body'] = df['body'].astype(str).apply(preprocess_text)

# ---- Save Cleaned Data ----
output_file = "C:/Users/johnj/ScrapyTest/ScrapyTest/FND-1/cleaned_nac.csv"
df.to_csv(output_file, index=False)

print(f"✅ Cleaned file saved to: {output_file}")
