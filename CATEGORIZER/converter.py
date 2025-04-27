import json
import csv

# Read NDJSON (newline-delimited JSON) — each line is its own JSON object
data = []
with open('C:/Users/johnj/ScrapyTest/ScrapyTest/FND-1/News_Category_Dataset_v3.json', 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

# Force category values to uppercase to avoid case mismatch
for item in data:
    if 'category' in item and item['category']:
        item['category'] = item['category'].upper()

# Group categories explicitly
entertainment = [item for item in data if item.get('category') == 'ENTERTAINMENT']
politics = [item for item in data if item.get('category') == 'POLITICS']
others = [item for item in data if item.get('category') not in ['ENTERTAINMENT', 'POLITICS']]

# Final sorted output
sorted_data = entertainment + politics + others

# Save to CSV
with open('output.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["link", "headline", "category", "short_description", "authors", "date"])
    writer.writeheader()
    writer.writerows(sorted_data)

