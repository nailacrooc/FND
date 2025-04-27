import pandas as pd

# Load your CSV file
input_file = "C:/Users/johnj/ScrapyTest/ScrapyTest/FND-2/bbc-text.csv"
output_file = "bbc-text3.csv"

# Read the CSV into a DataFrame
df = pd.read_csv(input_file)

# Ensure 'category' column exists
if "category" not in df.columns:
    raise ValueError("The CSV file must contain a 'category' column.")

# Normalize the category column for comparison
df["Category_normalized"] = df["category"].str.lower()

# Define the preferred order
preferred_order = ["entertainment", "politics", "sport", "tech", "business"]

# Create DataFrames for each preferred category
ordered_dfs = [df[df["Category_normalized"] == category] for category in preferred_order]

# Get remaining rows not in the preferred list
other_df = df[~df["Category_normalized"].isin(preferred_order)]

# Concatenate in order
sorted_df = pd.concat(ordered_dfs + [other_df], ignore_index=True)

# Drop the helper column
sorted_df.drop(columns=["Category_normalized"], inplace=True)

# Save the sorted DataFrame to a new CSV
sorted_df.to_csv(output_file, index=False)

print(f"Sorted CSV saved as '{output_file}'")
