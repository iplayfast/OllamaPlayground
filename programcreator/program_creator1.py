import json
import requests
import time
import ollama
import os
from typing import Dict, Any
import sys
import subprocess
from ollamaModel.Models import model_info

class Runner:
    def __init__(self):
        self.processes = {}
            
    def start_process(self, file, inputs=[]):
        args = ['python3', file] + inputs
        self.processes[file] = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return self.processes[file]
        
# Create an instance of the model_info class
models_instance = model_info()

# Retrieve and print model information
amodel = models_instance.get_model_by_name('mistral')
if amodel:
    model_name = amodel.get('name')
    print(f"Model name: {model_name}" if model_name else "Model name not found in the dictionary.")
else:
    print("Model not found.")

visual_models = models_instance.get_visual_models()
print(type(visual_models))

amodel = models_instance.get_model_by_name('mistral')
if amodel:
    model_name = amodel.get('name')
    print(f"Model name: {model_name}")
else:
    print("Model not found.")

task_template = {
    "Description": "",
    "Expected Output": "",
}

bool_template = {
    "Answer": False    
}

def query_ollama(query):
    message = [{
        'model': 'mistral',
        'format': 'json',  
        'stream': False,
        'role': 'user',
        'content': query,
    }]
    return ollama.chat(model='mistral', messages=message)

def get_list_of_models():
    return [item['name'] for item in ollama.list()['models']]

def filter_models_with_familytype(models_dict, family):
    return [model['name'] for model in models_dict['models'] if family in model['details'].get('families', [])]

def filter_models_with_familytype_search(models_dict, family):
    return [model['name'] for model in models_dict['models'] if any(family in f.lower() for f in model['details'].get('families', []))]

def get_list_of_embedding_models():
    return filter_models_with_familytype_search(ollama.list(), 'bert')

def get_list_of_visual_models():
    return filter_models_with_familytype(ollama.list(), 'clip')

def find_first_json(input_str: str):
    input_str = input_str.replace('\\', '')
    start_index = input_str.find('{')
    end_index = input_str.find('}') + 1
    return input_str[start_index:end_index] if start_index != -1 and end_index != -1 else ""

def parse_bool_response(response: str) -> bool:
    try:
        data = json.loads(response)
        return data.get("Answer", False)
    except json.JSONDecodeError:
        return parse_bool_response(find_first_json(response))

def matches_template(item, template):
    return all(key in item and isinstance(item[key], type(value)) for key, value in template.items()) and item["Description"] and item["Expected Output"]

def normalize_keys(keys_set):
    return {key.lower() for key in keys_set}

def validate_response_format(message: str, template: Dict[str, Any]) -> bool:
    try:
        template_keys = normalize_keys(json.loads(template).keys())
        return all(normalize_keys(item.keys()) == template_keys for item in json.loads(message))
    except (json.JSONDecodeError, AttributeError):
        return False

def expand_subtasks(subtasks):
    for task in subtasks:
        prompt = f"True or False, Someone doing the following task \"{task['Description']}\" would need to look at graphics. Answer True or False only."
        output_instructions = " Use the following json template for your answer: {template}"
        response = ask_ollama_for_json_response(prompt, task['Description'], output_instructions, json.dumps(bool_template))
        task['Use Graphics'] = parse_bool_response(response['message']['content'])
        task['Use Tools'] = ""
    return subtasks

def get_response_list(response):
    try:
        return json.loads(response["message"]["content"])
    except (json.JSONDecodeError, KeyError):
        return []

def print_list(title, items):
    print(title)
    if items:
        for item in items:
            for key, value in item.items():
                print(f"{key}: {value}")
    else:
        print("None found.")

def FormatPrompt(prompt, task, output_instructions, template):
    stemplate = json.dumps(template) if isinstance(template, dict) else template.replace('"', '\\"')
    formatted_prompt = prompt.replace('{task}', task).replace('{template}', stemplate)
    return formatted_prompt + output_instructions

def ask_ollama_for_json_response(query, task, output_instructions, template):
    prompt = FormatPrompt(query, task, output_instructions, template)
    response = query_ollama(prompt)
    max_attempts = 10
    while not validate_response_format(response['message']['content'], template) and max_attempts > 0:
        max_attempts -= 1
        new_query = f"Please only provide an answer to this question using the json format provided. The question was: '{query}'"
        prompt = FormatPrompt(new_query, task, output_instructions, template)
        response = query_ollama(prompt)
    return response

def ask_ollama_for_subtasks(task):
    task_templatedump = json.dumps(task_template)
    response = ask_ollama_for_json_response(
        "Create a list of subtasks to accomplish {task}, do not include any other information",
        task, " Use the following json template for your answer: {template}", task_templatedump
    )
    return get_response_list(response)

def ask_ollama_for_experts(task):
    response = ask_ollama_for_json_response(
        "Create a list of experts would be needed to create a program {task}, do not include any other information",
        task, " Use the following json template for your answer: {template}", json.dumps(bool_template)
    )
    return get_response_list(response)

# Main logic
task = "story writing application"
models_instance = model_info()

if os.path.exists('models.json'):
    with open('models.json', 'r') as f:
        existing_models = json.load(f)
else:
    existing_models = []

new_models = ollama.list()
model_dict = {model['name']: {"rating": 1, "category": model['details'].get('families', '') or model['details'].get('family', '')} for model in new_models['models']}

for model in list(existing_models):
    if model["name"] not in model_dict:
        existing_models.remove(model)
    else:
        model.update(model_dict[model["name"]])

for model_name, model_data in model_dict.items():
    if {"name": model_name} not in existing_models:
        existing_models.append({"name": model_name, "rating": 1, "category": model_data["category"]})

with open('models.json', 'w') as f:
    json.dump(existing_models, f, indent=4)

visual_models = get_list_of_visual_models()
print(visual_models)

embedding_models = get_list_of_embedding_models()
print(embedding_models)
