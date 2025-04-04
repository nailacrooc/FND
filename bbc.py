import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC  # Support Vector Classifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

# Load your dataset
dataset = pd.read_csv("C:/Users/johnj/ScrapyTest/ScrapyTest/FND-1/bbc-text.csv")

# Define the feature (text) and target (category)
X = dataset['text']  # Use the 'text' column as the feature
y = dataset['category']  # Use the 'category' column as the target

# Convert the text data to numerical data using TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words='english')  # Optional: 'stop_words' removes common words
X_tfidf = vectorizer.fit_transform(X)

# Split the data into training and testing sets (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# Initialize the model (Support Vector Machine in this case)
model = SVC(kernel='linear', random_state=42)  # 'linear' kernel is used here for simplicity

# Train the model
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Calculate evaluation metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='macro')  # Adjusted for multi-class
recall = recall_score(y_test, y_pred, average='macro')  # Adjusted for multi-class
f1 = f1_score(y_test, y_pred, average='macro')  # Adjusted for multi-class
conf_matrix = confusion_matrix(y_test, y_pred)

# Print the evaluation metrics
print(f'Accuracy: {accuracy}')
print(f'Precision: {precision}')
print(f'Recall: {recall}')
print(f'F1 Score: {f1}')
print(f'Confusion Matrix:\n{conf_matrix}')

# ---- USER INPUT PREDICTION ----
def predict_category():
    user_input = input("\nEnter a news article: ")  # Get user input
    
    # Transform user input using the same TF-IDF vectorizer
    user_input_tfidf = vectorizer.transform([user_input])
    
    # Predict the category
    predicted_category = model.predict(user_input_tfidf)[0]
    
    # Limit categories to Politics, Health, or Entertainment; else mark as 'Others'
    allowed_categories = {'politics', 'health', 'entertainment'}
    final_category = predicted_category if predicted_category in allowed_categories else 'others'
    
    # Output the predicted category
    print(f"\nPredicted Category: {final_category}")

# Call the function to take user input and predict
predict_category()
