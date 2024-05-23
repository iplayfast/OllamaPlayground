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
        if os.path.exists('models.json'):
            with open('models.json', 'r') as f:
                models_on_disk = json.load(f)
        else:
            models_on_disk = []
    
        ollama_models = ollama.list()
        for ollama_model in ollama_models['models']:
            category = ollama_model['details'].get('families', '') if 'details' in ollama_model else ''
            if category == None:
                category = ollama_model['details'].get('family', '') if 'details' in ollama_model else ''
            size = 1.0 - 1.0 / (ollama_model['size']/1073741822.0)
            rating = size # default value
            model_name = ollama_model['name']
            self.models[ollama_model['name']] = {"name": model_name, "rating": rating,"size":size, "category": category}
        # Update the existing models with the new ones, removing any that are no longer present
        for model_from_disk in list(models_on_disk): 
            if ollama_model["name"] not in self.models:
                models_on_disk.remove(model_from_disk)
            else: 
                model_from_disk.update(self.models[model_from_disk["name"]])

        # Add any new models to the existing list
        for model_name in self.models:
            if {"name": model_name} not in models_on_disk:
                ollama_model = self.models.get(model_name)                
                rating = ollama_model.get('rating')
                size = ollama_model.get('size')
                category = ollama_model.get('category')                
                models_on_disk.append({"name": model_name, "rating": rating, "size": size, "category": category}) 
                
        # Save the updated list back to the JSON file
        with open('models.json', 'w') as f: 
            json.dump(models_on_disk, f, indent=4)        
    def get_best_model_by_category(self, target_category: str) -> dict:
        best_model = None
        best_rating = 0
        best_size = float('inf')
        for model in self.models.values():
            if isinstance(model, dict):                
                categories = model.get("category", [])
                if not isinstance(categories, list):
                    categories = [categories]
                if target_category in categories:
                    rating = model["rating"]
                    size = model["size"]
                    if rating > best_rating or (rating == best_rating and size < best_size):
                        best_model = model
                        best_rating = rating
                        best_size = size
        return best_model        

        
    def get_visual_models(self):
        return self.get_best_model_by_category('clip')
    
    def get_embedding_models(self):
        return self.get_best_model_by_category(self,'bert')
    

    def get_model_by_name(self, name: str) -> dict:
        """
        Returns the model dictionary for the given model name.
        If the model name is not found, returns None.
        """
        model = self.models.get(name)
        if not model:
            # If the model name is not found, try to find by removing the tag
            model_name_without_tag = name.split(':')[0]
            model = self.models.get(model_name_without_tag)
            if not model:
                # If still not found, try appending ':latest' tag
                model_name_with_latest_tag = name + ':latest'
                model = self.models.get(model_name_with_latest_tag)
        return model


    def oldget_model_by_name(self, name: str) -> dict:
        """
        Returns the model dictionary for the given model name.
        If the model name is not found, returns None.
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