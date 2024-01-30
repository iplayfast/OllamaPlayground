import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

def to_lowercase(item):
    if isinstance(item, dict):
        return {k: to_lowercase(v) for k, v in item.items()}
    elif isinstance(item, list):
        return [to_lowercase(i) for i in item]
    elif isinstance(item, str):
        return item.lower().strip()
    else:
        return item  # Return the item as is if it's not a string


def wrap_text(text, char_limit=80):
    words = text.split(' ')
    wrapped_text = '<b>'
    line_length = 0

    for word in words:
        if line_length + len(word) > char_limit:
            wrapped_text += '<br>'
            line_length = 0
        wrapped_text += word + ' '
        line_length += len(word) + 1
    wrapped_text += '</b>'
    return wrapped_text

def round_to_nearest_tenth(num):
    return round(num, 1)

def join_explanations(explanations):
    return '<br>'.join([wrap_text(explanation) for explanation in explanations])

# Load JSON data
with open('results.json', 'r') as file:
    data = json.load(file)

# Convert all data to lowercase
data_lowercase = to_lowercase(data)

# Now, data_lowercase contains all your data in lowercase
data = data_lowercase

# Prepare a list to hold the cleaned data
cleaned_data = []
for model, entries in data.items():
    for entry in entries:
        question = wrap_text(entry['question'])
        answer = wrap_text(entry['answer'])
        explanations = entry.get('explanation', [])  # Get explanations, default to empty list if not present
        wrapped_explanations = join_explanations(explanations)  # Process explanations
        answer_time = str(round_to_nearest_tenth(entry['answer_time'])) + ' sec'

        for criticism in entry['criticisms']:
            # Extract rating and category from criticism
            parts = criticism.split(" ")
            try:
                rating = int(parts[0])
                if rating>100: #bad data
                    rating = -1;

                category = " ".join(parts[1:])
                cleaned_data.append({
                    "Model": model,
                    "Question": question,
                    "Answer": answer,
                    "AnswerTime": answer_time,
                    "Rating": rating,
                    "Category": category,
                    "Explanation": wrapped_explanations  # Add explanations to each entry
                })
            except ValueError:
                # Handle cases where the first part is not a number
                continue

# Convert to DataFrame
df = pd.DataFrame(cleaned_data)

# Apply wrap_text function to each answer and question in your DataFrame
df['Answer'] = df['Answer'].apply(wrap_text)
df['Question'] = df['Question'].apply(wrap_text)
df['Explanation'] = df['Explanation'].apply(wrap_text)


fig = px.bar(df, x='Category', y='Rating', color='Model', barmode='group',
             hover_data=['Question', 'Answer', 'AnswerTime','Explanation'])

fig.show()

