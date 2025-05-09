import pandas as pd
import random

def shuffle_csv_rows(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Shuffle the rows
    shuffled_df = df.sample(frac=1, random_state=random.randint(0, 10000)).reset_index(drop=True)

    # Save the shuffled DataFrame to a new CSV file
    shuffled_df.to_csv(output_file, index=False)
    print(f"Shuffled data saved to {output_file}")

if __name__ == "__main__":
    # Example usage
    input_csv = "ALL_shuffled.csv"       # Replace with your actual CSV file
    output_csv = "ALL_shuffled_na.csv"   # Output file name
    shuffle_csv_rows(input_csv, output_csv)
