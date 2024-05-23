import json
import requests
import time
import ollama
import os
from typing import Dict, Any

# to run other python scripts
import sys
import subprocess
import os


from ollamaModel.Models import model_info




class Runner:
        def __init__(self):
            self.threads = []
            
        def start_process(self, file,inputs=[]):
            args = ['python3',file]
            for input in inputs:
                args.append(input)
            self.threads[file]=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            return self.threads[file]
        
""" example use 
target_file = sys.argv[1]
inputs = sys.argv[2:]

print(target_file)
print(inputs)
runner = Runner()
runner.start_process(target_file,inputs)

"""


 
    
        
        
        
# Create an instance of the model_info class
models_instance = model_info()

# Retrieve a model dictionary by name
amodel = models_instance.get_model_by_name('mistral')

# Check if the model is found
if amodel:
    # Retrieve the model name from the model dictionary
    model_name = amodel.get('name')

    # Print the model name if found
    if model_name:
        print(f"Model name: {model_name}")
    else:
        print("Model name not found in the dictionary.")
else:
    print("Model not found.")

om = model_info()
visual_models = om.get_visual_models()        
print(type(visual_models))
amodel = om.get_model_by_name('mistral')
print(type(amodel))
print("\n ok")
if amodel:
    model_name = amodel.get('name')
    print(f"Model name: {model_name}")
else:
    print("Model not found.")


        
        
task_template = {
    "Description": "",
    "Expected Output": "",
#    "Use Graphics": False,
#    "Tools needed": ""
}
bool_template = {
    "Answer": False    
}
# Function to send query and get response from Ollama API using 'requests' library
def query_ollama(query):
    message = [
        {
            'model': 'mistral',
            'format': 'json',  
            'stream': False,
            'role': 'user',
            'content': query,
        },
    ]
    response = ollama.chat(model='mistral', messages=message)
    return response

def get_list_of_models():    
    l = ollama.list()
    names = [item['name'] for item in l['models']]
    return names

def filter_models_with_familytype(models_dict, family):
    """
    Filter models based on a given family type.
    Args:
        models (list): A list of dictionaries containing information about models.
        family (str): The family type to filter the models.
    Returns:
        list: A filtered list of models with the specified family type.
    """
    models_with_family = []
    for model in models_dict['models']:
        families = model['details'].get('families')
        if families is not None and family in families:
            models_with_family.append(model['name'])
    return models_with_family

def filter_models_with_familytype_search(models_dict, family):
    """
    Filter models based on a given family type.
    Args:
        models (list): A list of dictionaries containing information about models.
        family (str): The family type to filter the models.
    Returns:
        list: A filtered list of models with the specified family type.
    """
    models_with_family = []
    for model in models_dict['models']:
        families = model['details'].get('families')
        if families is not None:
            for f in families:
                if (family in f.lower()) or (family.lower() in f.lower()):
                    models_with_family.append(model['name'])
    return models_with_family

def get_list_of_embedding_models():
    l = ollama.list()
    return filter_models_with_familytype_search(l,'bert')
def get_list_of_visual_models():
    l = ollama.list()
    return filter_models_with_familytype(l,'clip')
    
def find_first_json(input_str: str):
    """
    Loads JSON content from the input string until an error occurs.

    Args:
        input_str (str): The input string containing JSON content followed by other text.

    Returns:
        list: List of JSON objects extracted from the input string.
    """
    json_objects = []
    input_str = input_str.replace('\\', '')
    while input_str:
        try:
            # Try to find the start of JSON content
            start_index = input_str.index('{')
            # Find the end of JSON content
            end_index = input_str.index('}') + 1
            # Extract JSON content            
            json_str = input_str[start_index:end_index]
            return json_str
            # Parse JSON content
            json_obj = json.loads(json_str)
            # Add JSON object to the list
            json_objects.append(json_obj)
            # Update input string to remove processed JSON content
            input_str = input_str[end_index:]
        except ValueError:
            # If JSON content is not found, break the loop
            break
        except json.JSONDecodeError:
            # If there's an error parsing JSON, skip this JSON content
            input_str = input_str[end_index:]
    
    return json_objects

# Function to parse JSON response from Ollama API
def parse_bool_response(response: str) -> bool:
    """
    Parses the JSON response string and returns a boolean based on the value of the "Answer" key.

    Args:
        response (str): The JSON response string.

    Returns:
        bool: The boolean value based on the "Answer" key in the response.
    """
    try:
        if len(response)<12: # need at least 12 characters            
            return False
        # Parse the JSON string
        data = json.loads(response)
        # Check if "Answer" key exists and its value is True
        if "Answer" in data and isinstance(data["Answer"], bool):
            return data["Answer"]
        else:
            # If "Answer" key is missing or its value is not boolean, return False
            return False
    except json.JSONDecodeError:
        response = find_first_json(response)
        return parse_bool_response(response)   
    return False

def matches_template(item, template):
    # Check if item has all keys in template and they match the template's types
    for key, value in template.items():
        if key not in item or not isinstance(item[key], type(value)):
            return False
    # Check if Description and Expected Output are non-empty strings
    if not item["Description"] or not item["Expected Output"]:
        return False
    return True

def normalize_keys(keys_set):
    """
    Normalize the case of keys in a set.
    """
    return {key.lower() for key in keys_set}

def validate_response_format(message: str, template: Dict[str, Any]) -> bool:
    """
    Validates if a given response adheres to a specified JSON template format.

    Args:
        response (Any): The response to be validated, which can be a dictionary or a JSON string.
        template (dict): The JSON template dictionary.

    Returns:
        bool: True if the response adheres to the template format, False otherwise.
    """
    
    thetype = type(template)
    if thetype==dict:
        template = str(template)
        thetype = type(template)
    if thetype!=str:
        return False
    jtemplate = json.loads(template) #jtemplate is 'dict'
    try:
        jmessage = json.loads(message)  #jmessage is 'dict'
    except json.decoder.JSONDecodeError as e:
        return False
    template_keys = normalize_keys(jtemplate.keys())
    
    for r in jmessage:        
        if (type(r)==str):
            rkeys = {r.lower()}
        else:
            rkeys = normalize_keys(r.keys())        
        if set(rkeys)!=set(template_keys):
            return False
    return True
    
def expand_subtasks(subtasks):
    for task in subtasks:
        prompt = "True or False, Someone doing the following task \"{task}\" would need to look at graphics. Answer True or False only."

        output_instructions = " Use the following json template for your answer: {template}"
        
        response = ask_ollama_for_json_response(prompt,task['Description'],output_instructions,json.dumps(bool_template))
        task['Use Graphics'] = parse_bool_response(response['message']['content'])
        #task['View Graphics'] = False
        task['Use Tools'] = ""  #todo
    return subtasks
    
    
def test_validate_response_format():
    response = {'model': 'mistral', 'created_at': '2024-04-01T14:06:10.307745227Z', 'message': {'role': 'assistant', 'content': ' [\n  {\n    "Description": "Collect real-time weather data from various sources (e.g., meteorological agencies, APIs)",\n    "Expected Output": "Up-to-date weather data in a structured format"\n  },\n  {\n    "Description": "Process and analyze collected weather data using statistical methods and machine learning algorithms",\n    "Expected Output": "Weather patterns, trends, and forecasts"\n  },\n  {\n    "Description": "Design user interface for displaying weather information in an easy-to-understand format (icons, graphs, etc)",\n    "Expected Output": "Intuitive and visually appealing interface"\n  },\n  {\n    "Description": "Implement location services to provide accurate weather forecasts based on user location",\n    "Expected Output": "Automatically generated forecasts for user\'s current location"\n  },\n  {\n    "Description": "Develop a system for real-time alerts and notifications for extreme weather conditions",\n    "Expected Output": "Timely warnings for severe weather events (e.g., storms, hurricanes)"\n  },\n  {\n    "Description": "Create an API or webhook for third-party developers to integrate the application\'s forecasts and data into their own projects",\n    "Expected Output": "Accessible and versatile platform for developers"\n  },\n  {\n    "Description": "Implement a system for storing historical weather data for analysis and trend identification",\n    "Expected Output": "Robust database for long-term weather tracking and forecasting"\n  }\n]'}, 'done': True, 'total_duration': 3803960026, 'load_duration': 714772715, 'prompt_eval_count': 53, 'prompt_eval_duration': 63346000, 'eval_count': 356, 'eval_duration': 3025335000}
    
    template = '{"Description": "", "Expected Output": ""}'
    b = validate_response_format(response,template)
    print(b)    
    
def get_response_list(response):
    # Function to get subtasks from Ollama's JSON response
    if "message" in response and "content" in response["message"]:
        message = response["message"]["content"]
        jmessage = json.loads(message)
#        print(type(jmessage))
        return jmessage        
    return None

def print_list(title,list):
    print(title)
    if list:        
        for item in list:
            for key,value in item.items():
                print(f"{key}: {value}")
            #print(type(subtask))
            #print(f"Description: {subtask['Description']}")
            #print(f"Expected output: {subtask['Expected Output']}\n")
    else:
        print("None found.")


def FormatPrompt(prompt, task, output_instructions, template):
    """
    Format the prompt with task and template parameters.

    Args:
        prompt (str): The original prompt.
        task (str): The task to insert into the prompt.
        template (str or dict): The template to insert into the prompt.

    Returns:
        str: Formatted prompt with task and template parameters.
    """
    if isinstance(template, dict):
        stemplate = json.dumps(template)
    else:
        # Escape double quotes in the template string
        stemplate = template.replace('"', '\\"')

    # Escape curly braces in the prompt string
    #formatted_prompt = prompt.replace('{', '{{').replace('}', '}}').format(task=task, template=stemplate)
    formatted_prompt = prompt.replace('{task}',task);
    formatted_prompt += output_instructions;
    formatted_prompt = formatted_prompt.replace('{template}',stemplate);
    return formatted_prompt

def test_format_prompt():
    prompt = 'You responded with \' {"Answer": true}\n\nExplanation: While it\'s possible to collect real-time weather data from various sources programmatically, the need to examine graphics (like satellite imagery or radar) is a visual task that cannot be directly automated with code alone. However, many meteorological agencies and services provide APIs for accessing their data, which can be integrated into software systems for automated data collection.\'. Please provide a answer using only the proper json template.{task} requires looking at graphics. Answer True or False only.            \nUse the following json template for your answer: {template}'
    task = 'Collect real-time weather data from various sources (e.g., meteorological agencies, satellite imagery)'
    template = '{"Answer": false}'
    result = FormatPrompt(prompt,task,template)
    
def ask_ollama_for_json_response(query,task,output_instructions, template):
    prompt = FormatPrompt(query,task,output_instructions,template)
    response = query_ollama(prompt) # response is a 'dict'    
    max_times = 10
    while (not validate_response_format(response['message']['content'], template)):
        r = response['message']['content']
        max_times -= 1
        if (max_times==0):  #give up
            break;
        newquery = "Please only provide an answer to this question using the json format provided. The question was: '"        
        newquery += query        
        newquery += "'"
        prompt = FormatPrompt(newquery,task,output_instructions,template)
        response = query_ollama(prompt)
    return response

    
def ask_ollama_for_subtasks(task):
    task_templatedump = json.dumps(task_template)
    response = ask_ollama_for_json_response("Create a list of subtasks to accomplish {task},\
do not include any other information",
                                 task," Use the following json template for your answer: {template}",task_templatedump)
    return get_response_list(response)                   
    

# Function for main logic of asking Ollama for experts needed for a specific task
def ask_ollama_for_experts(task):
    response = ask_ollama_for_json_response("Create a list of experts would be needed to create a program {task},\
do not include any other information",
                                 task," Use the following json template for your answer: {template}",json.dumps(expert_template))    
    experts = get_response_list(response)
    return experts

# Ask Ollama for experts needed to create a specific program
task = "story writing application"

models = model_info()

# Load existing models from JSON file, or create an empty list if the file doesn't exist
if os.path.exists('models.json'):
    with open('models.json', 'r') as f:
        existing_models = json.load(f)
else:
    existing_models = []


#test_validate_response_format()
#test_format_prompt()

#subtask = ask_ollama_for_subtasks(task)
#subtask = expand_subtasks(subtask)  # add graphics and tools
#print(f"To create {task}, the following subtasks are needed according to Ollama:")
#print_list("List of subtasks:",subtask)


#experts = ask_ollama_for_experts(task)
#print(f"To create {task}, the following experts are needed according to Ollama:")
#print_list("List of experts:",experts)

#new_models = get_list_of_models()
#print(new_models)
new_models = ollama.list()



# Create a dictionary to map model names to their ratings and categories
model_dict = {}
for model in new_models['models']: 
    category = model['details'].get('families', '') if 'details' in model else ''
    if (category==None):
        category = model['details'].get('family', '') if 'details' in model else ''
    model_dict[model['name']] = {"rating": 1, "category": category}

# Update the existing models with the new ones, removing any that are no longer present
for model in list(existing_models): 
    if model["name"] not in model_dict:
        existing_models.remove(model)
    else: 
        model.update(model_dict[model["name"]])

# Add any new models to the existing list
for model_name in model_dict:
    if {"name": model_name} not in existing_models:
        existing_models.append({"name": model_name, "rating": 1, "category": model_dict[model_name]["category"]})

# Save the updated list back to the JSON file
with open('models.json', 'w') as f: 
    json.dump(existing_models, f, indent=4)




new_models = get_list_of_visual_models()
print(new_models)

new_models = get_list_of_embedding_models()
print(new_models)
