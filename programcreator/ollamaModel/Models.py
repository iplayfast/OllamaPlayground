   
import json
import requests
import time
import ollama
import os
from typing import Dict, Any

class model_info:
    def __init__(self):
        self.models = {}
        self.load_models()
        
    def load_models(self):
        """
        Load models from the 'models.json' file and populate the self.models dictionary.
        If no such file exists, initialize the list of models to an empty list.
        """
        if os.path.exists('models.json'):
            with open('models.json', 'r') as f:
                # Read the existing list of models from the JSON file
                models_in_json_file = json.load(f)
        else:
            # Initialize the list of models if no such file exists
            models_in_json_file = []

        ollama_models = ollama.list()
        
        for ollama_model in ollama_models['models']:
            """
            Process each model from Ollama, calculating its rating and size,
            and adding it to the self.models dictionary.
            """
            category = ollama_model['details'].get('families', '') if 'details' in ollama_model else ''
            if category == None:
                category = ollama_model['details'].get('family', '') if 'details' in ollama_model else ''
            
            size = 1.0 - 1.0 / (ollama_model['size']/1073741822.0)
            rating = size # default value
            model_name = ollama_model['name']
            self.models[ollama_model['name']] = {"name": model_name, "rating": rating,"size":size, "category": category}

        """
        Update the existing models with the new ones, removing any that are no longer present.
        Add any new models to the existing list.
        Save the updated list back to the JSON file.
        """
        for model_from_json_file in list(models_in_json_file): 
            if ollama_model["name"] not in self.models:
                # Remove the model from the JSON file if it's no longer present
                models_in_json_file.remove(model_from_json_file)
            else: 
                try:
                    # Update the existing model with new values
                    self.models[model_from_json_file["name"]].update(model_from_json_file)
                except KeyError:
                # The model is still present in the JSON file, but its corresponding key was removed from self.models
                    models_in_json_file.remove(model_from_json_file)

        for model_name in self.models:
            if {"name": model_name} not in models_in_json_file:
                ollama_model = self.models.get(model_name)                
                rating = ollama_model.get('rating')
                size = ollama_model.get('size')
                category = ollama_model.get('category')                
                models_in_json_file.append({"name": model_name, "rating": rating, "size": size, "category": category}) 
                
        with open('models.json', 'w') as f: 
            # Save the updated list of models back to the JSON file
            json.dump(models_in_json_file, f, indent=4)        
    def get_best_model_by_category(self, target_category: str) -> dict:
        """
        Returns the model with the highest rating and smallest size within a given category.
        If no models are found in that category, returns None.
        """
        best_model = None
        best_rating = 0
        best_size = float('inf')
        for model in self.models.values():
            if isinstance(model, dict):                
                categories = model.get("category", [])
                if isinstance(categories, str):
                    categories = [categories]
                for category in categories:
                    if category == target_category:
                        rating = model.get('rating', 0)
                        size = model.get('size', float('inf'))
                        if rating > best_rating or (rating == best_rating and size < best_size):
                            best_model = model
                            best_rating = rating
                            best_size = size
        return best_model


    def get_model_by_name(self, name: str) -> dict:
        """
        Returns the model dictionary for the given model name.
        If the model name is not found, returns None.
        It also tries to find the model by removing the tag (if present)
        and appending ':latest' tag if necessary.
        """
        model = self.models.get(name)
        if not model:
            # Split the name at the colon `:` and try to get the model with the first part
            model_name_without_tag = name.split(':')[0]
            model = self.models.get(model_name_without_tag)
        if not model:
            model_name_with_latest_tag = name + ':latest'
            model = self.models.get(model_name_with_latest_tag)            
        return model


    def oldget_model_by_name(self, name: str) -> dict:
        """
        Returns the model dictionary for the given model name.
        If the model name is not found, returns None.
        It also tries to find the model by removing the tag (if present)
        and appending ':latest' tag if necessary.
        """
        amodel = self.models.get(name)
        if not amodel:
            # Split the name at the colon `:` and try to get the model with the first part
            model_name_without_tag = name.split(':')[0]
            amodel = self.models.get(model_name_without_tag)
        if not amodel:
            model_name_with_latest_tag = name + ':latest'
            amodel = self.models.get(model_name_with_latest_tag)            
        return amodel
