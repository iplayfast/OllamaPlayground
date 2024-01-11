#create notes
import requests
from langchain.llms import Ollama

import os
import json
import requests
import hashlib
from pathlib import Path

import pandas as pd 
import numpy as np 
import re
import time

BASE_URL = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')

CriticOllama = Ollama(base_url='http://localhost:11434',model="mistral",verbose=False,temperature=0.0)
#CriticOllama = Ollama(base_url='http://localhost:11434',model="tinyllama",verbose=False,temperature=0.0)

def save_results_to_file(results, filename='results.json'):
    """Save the current state of results to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=4)

def get_model_list():
    try:
        response = requests.get(f"{BASE_URL}/api/tags")
        response.raise_for_status()
        data = response.json()
        models = data.get('models', [])
        
        # Sort the list of models by size (largest to smallest)
        sorted_models = sorted(models, key=lambda x: x['size'], reverse=True)

        return sorted_models
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

import concurrent.futures

def get_answer(ollama, question, timeout=1000):
    start_time = time.time()
    result = ''
    """Get an answer from the Ollama model with a timeout."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(ollama, question)
        try:
            result = future.result(timeout=timeout).strip()
        except concurrent.futures.TimeoutError:
            print(f"Timed out after {timeout} seconds for question: {question}")
            result = 'No Answer due to timeout'
        except Exception as e:
            print(f"Error: {e}")
            result =  'No Answer due to error'
    end_time = time.time()
    elapsed_time = end_time - start_time
    return result.strip(), elapsed_time
# Usage in your loop remains the same

def extract_code(content):
    # Regular expression to match content within triple backticks, ignoring language specifier
    pattern = r"```(?:[^\r\n]+)?\n(.*?)```"

    # Find all non-overlapping matches in the string
    matches = re.findall(pattern, content, re.DOTALL)
    
    if matches:
        extracted_content = ""
        for match in matches:
            # Add each match to the result with a newline in between
            extracted_content += f"{match}\n\n"
        
        return extracted_content.strip()  # Remove trailing newlines
    else:
        return None

    
def get_criticism(category, question_text, answer,critics_answer,special_instructions=None):    
    if (len(critics_answer)>0):
        critics_answer = "You believe the best answer is '" + critics_answer + "' "
    if (category=='code correctness'):
        answer = extract_code(answer)
        if (answer is None):
            return '0 code correctness', 'no code'
        prompt = (
            f"Evaluate the following code contained between lines of triple ticks (```) for correctness as a result of the question '{question_text}'. The code answer is '{answer}'. "
            "Rate the answer on a scale from 1 to 100. Explain your reasoning for your rating. "            
            "If the answer does have code, rate the code from 1 to 100 in how correct it is in answering the question."
            f"Always format your answer in the form of 'rating {category} reason'"
            f"For example, if you think the answer is correct, reply '100 {category}' followed by the reason "
            f"For example, if you think the answer is incorrect, reply '1 {category}' followed by the reason "
            f"For example, if the answer contains no python, c++ or other programming language code reply '0 {category} no code' followed by the reason "
        )
    else:
        prompt = (
    f"Rate the answer below on a scale from 1 to 100, where 1 is the worst and 100 is the best. Explain your reasoning for your rating. "
    f"The category is '{category}', and the question was '{question_text}'. "
    f"Answer: '{answer}'.  {critics_answer}"
    "Provide your rating as a single number followed by the category followed by the reason, do not consider any other categories."
    "An answer that does not apply to the category should receive a rating of '0 N/A' followed by the reason "
    "For example, if you think the answer is sincere and not humorous at all and the category is 'humor', reply '0 N/A not humorous at all' "    
    f"For example, if you think the answer in the {category} category is excellent, reply '100 {category}' followed by the reason "    
    f"For example, if you think the answer in the {category} category is barely acceptable, reply '1 {category}' followed by the reason "
    f"For example, if you think the answer in the {category} category is acceptable but could be better, reply '50 {category}' followed by the reason "
    "If you cannot rate the answer or feel the category does not apply to the answer, reply '0 N/A' followed by the reason "        
    "If the answer answers the question correctly, give your rating at least a 10 "
    "Ratings should be in a range 1 to 100, with 1 being the worst and 100 being the best. "
    f"Explain your reasoning or your rating. {special_instructions}"
)

    #explanation,elapsed_time = get_answer(mistral_ollama, prompt)    
    explanation,elapsed_time = get_answer(CriticOllama, prompt)    
    
    #rating =  get_answer(mistral_ollama, prompt).strip() 
    
    if explanation.__contains__('No Answer'):
        explanation = '0 ' + explanation    
    # Regular expression to find all numbers
    numbers = re.findall(r'\d+', explanation)
    if not numbers:
        numbers = ['0']
    rating = numbers[0] + ' ' + category  
    return rating, explanation


def load_questions(filename):
    """Load questions and answers from a JSON file."""
    with open(filename, 'r') as file:
        return json.load(file)

def round_to_nearest_tenth(num):
    return round(num, 1)

# Usage in your loop

l = get_model_list()
#l = l[1:3]

allfiles = os.listdir()
qfiles = sorted([f for f in allfiles if f.startswith('q')])
critic_cats = ['Humor','Sincerity','Logic','code correctness','Simplicity','accuracy','complexity','legality']
"""
print("Attempting to load each model to see if they can be loaded")
for model in l:
    model_name = model['name']
    print(f"   attempting to load model {model_name}")
    ollama = Ollama(base_url='http://localhost:11434',model=model_name)
    answer, elapsed = get_answer(ollama,'are you there',300) #timeout is 5 minutes
    if answer.__contains__('No Answer'):
        l.remove(model)
    
    loaded = '------------not loaded------------' if answer.__contains__('No Answer') else 'loaded'
    answer_time = str(round_to_nearest_tenth(elapsed))
    print(f"         model {model_name} {loaded} in {answer_time} seconds")    
    
print("Only working models are tested")
"""
results = {}
for model in l:
    model_name = model['name']
    questions = []
    answers = []
    critisiums = []
    print(model_name)
    ollama = Ollama(base_url='http://localhost:11434',model=model_name)
    questions_and_answers = load_questions('questions.json')    
    timeout = 5000 # first timeout is longer to allow the model to load
    for qa in questions_and_answers:
        question_text = qa['question'].strip()
        correct_answer = qa['answer'].strip()        
        special_instructions = qa['special_instructions'].strip()
        answer,answer_time = get_answer(ollama, question_text, timeout)
        timeout = 1500 # second timeout is shorter since the model is ready
        criticisms = []
        explanations = []
        # Iterate over each category and get criticism and explanation
        for cat in critic_cats:
            rating, explanation = get_criticism(cat, question_text, answer, correct_answer,special_instructions)
            criticisms.append(rating)
            explanations.append(explanation)
            
                # Store the results
        results.setdefault(model_name, []).append({
            'question': question_text,
            'answer': answer,
            'answer_time': answer_time,
            'criticisms': criticisms,
            'explanation': explanations
        })                    
            
            #    critic = f'In the following category "{c}" give a rating from 1 to 10 with 10 being the best and 1 being the worst of the following answer "{answer}" to the question "{question_text}". Just the number.'                            
        save_results_to_file(results)

    save_results_to_file(results)

        