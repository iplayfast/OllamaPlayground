import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
    wrapped_text = ''
    line_length = 0

    for word in words:
        if line_length + len(word) > char_limit:
            wrapped_text += '<br>'
            line_length = 0
        wrapped_text += word + ' '
        line_length += len(word) + 1

    return wrapped_text

def round_to_nearest_tenth(num):
    return round(num, 1)


# Load JSON data
with open('results.json', 'r') as file:
    data = json.load(file)

# Convert all data to lowercase
data_lowercase = to_lowercase(data)

# Now, data_lowercase contains all your data in lowercase
data = data_lowercase

# Prepare a list to hold the cleaned data
cleaned_data = []

# Process the data
for model, entries in data.items():
    for entry in entries:
        question = entry['question']
        answer = entry['answer']
        answer_time = str(round_to_nearest_tenth(entry['answer_time'])) + ' sec'
        for criticism in entry['criticisms']:
            # Extract rating and category from criticism
            parts = criticism.split(" ")
            try:
                rating = int(parts[0])
                category = " ".join(parts[1:])
                cleaned_data.append({
                    "Model": model,
                    "Question": question,
                    "Answer": answer,
                    "AnswerTime": answer_time,
                    "Rating": rating,
                    "Category": category
                })
            except ValueError:
                # Handle cases where the first part is not a number
                continue

# Convert to DataFrame
df = pd.DataFrame(cleaned_data)


# Create a subplot environment with 2 rows and 1 column
fig, axes = plt.subplots(2, 1, figsize=(15, 20))

# Plot the bar plot in the first subplot
sns.barplot(x='Category', y='Rating', hue='Model', data=df, ax=axes[0])
axes[0].set_title('Average Rating per Category by Model')
axes[0].tick_params(axis='x', rotation=45)

# Plot the heatmap in the second subplot
pivot_table = df.pivot_table(values='Rating', index='Model', columns='Category', aggfunc='mean')
sns.heatmap(pivot_table, annot=True, cmap='coolwarm', ax=axes[1])
axes[1].set_title('Heatmap of Average Ratings per Category by Model')
axes[1].set_xlabel('Category')
axes[1].set_ylabel('Model')
axes[1].tick_params(axis='x', rotation=45)
axes[1].tick_params(axis='y', rotation=0)

# Adjust layout for better spacing
plt.tight_layout()

# Show the plots
plt.show()
plt.figure(figsize=(15, 6))
sns.scatterplot(data=df, x='Category', y='Rating', hue='AnswerTime', style='Model')
plt.title('Ratings vs Category with Answer Time')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

import plotly.express as px

# Assuming df is your DataFrame

# Apply the function to each answer in your DataFrame
df['WrappedAnswer'] = df['Answer'].apply(wrap_text)
df['WrappedQuestion'] = df['Question'].apply(wrap_text)

# Now, use 'WrappedAnswer' in your Plotly hover data
fig = px.bar(df, x='Category', y='Rating', color='Model', barmode='group',
             hover_data=['Question', 'WrappedAnswer', 'AnswerTime'])

fig.show()

