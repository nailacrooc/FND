import json
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pickle

# Step 1: Train LDA Model
def train_lda(file_path):
    print("Starting LDA model training...")

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)  # Try loading as a JSON array
        except json.JSONDecodeError:
            f.seek(0)  # Reset file pointer
            data = [json.loads(line) for line in f]

    df = pd.DataFrame(data)

    # Ensure required columns exist
    if "category" not in df.columns or "short_description" not in df.columns:
        raise ValueError("Dataset must contain 'category' and 'short_description' columns.")

    # Preprocess text data (convert to lowercase)
    texts = [str(text).lower() for text in df["short_description"] if isinstance(text, str)]

    # Convert text data into a document-term matrix
    vectorizer = CountVectorizer(stop_words='english')
    doc_term_matrix = vectorizer.fit_transform(texts)

    # Train LDA Model
    num_topics = len(df["category"].unique())  # One topic per category
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(doc_term_matrix)

    # Save trained model and vectorizer for later use
    with open("lda_model.pkl", "wb") as f:
        pickle.dump(lda, f)

    with open("vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)

    print("LDA model training complete. Model saved.")

    # Return the category mapping
    category_mapping = {i: cat for i, cat in enumerate(df["category"].unique())}
    return category_mapping

# Step 2: Predict Categories
def predict_categories(new_file_path, category_mapping):
    print("Loading trained model and vectorizer for prediction...")

    # Load trained LDA model and vectorizer
    with open("lda_model.pkl", "rb") as f:
        lda = pickle.load(f)

    with open("vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)

    # Load new CSV file
    new_df = pd.read_csv(new_file_path)

    # Ensure required text column exists
    if "Content" not in new_df.columns:
        raise ValueError("New dataset must contain a 'Content' column.")

    # Preprocess new text data (convert to lowercase)
    new_texts = [str(text).lower() for text in new_df["Content"] if isinstance(text, str)]

    # Transform new data using the saved vectorizer
    new_doc_term_matrix = vectorizer.transform(new_texts)

    print("Predicting topics for the new articles...")

    # Predict topic distributions using the trained LDA model
    topic_distributions = lda.transform(new_doc_term_matrix)

    # Assign category based on the most probable topic
    predicted_categories = topic_distributions.argmax(axis=1)

    # Map topic indices back to category names using the passed category_mapping
    new_df["predicted_category"] = [category_mapping[i] for i in predicted_categories]

    # Update categories to "Others" if not Politics, Health, or Entertainment
    valid_categories = ["politics", "health", "entertainment"]
    new_df["predicted_category"] = new_df["predicted_category"].apply(
        lambda x: x if x in valid_categories else "Others"
    )

    # Save predictions to a new CSV file
    new_df.to_csv("predicted_categories.csv", index=False)

    print("Prediction complete. Results saved in 'predicted_categories.csv'.")

# Main block to call the functions
if __name__ == "__main__":
    print("Script started...")

    # Train the model first and get the category mapping
    print("Training LDA model...")
    category_mapping = train_lda("C:/Users/johnj/ScrapyTest/ScrapyTest/FND/News_Category_Dataset_v3.json")

    # After training, predict categories
    print("Starting prediction for new articles...")
    predict_categories("C:/Users/johnj/ScrapyTest/ScrapyTest/FND/for_lda.csv", category_mapping)
    
    print("Script execution complete.")
