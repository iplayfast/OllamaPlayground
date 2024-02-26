import json
import os

import requests
from langchain.tools import tool

class SearchTools():
    @tool("Search the internet")
    def search_internet(query):
        """Useful to search the internet about a given topic an return relevant results"""
        print("Searching the internet...")
        top_result_to_return = 5
        url = "https://google.serper.dev/search"
        payload = json.dumps(
            {"q": query,"num": top_result_to_return, "tbm": "nws"})
        headers = {
            #'X-API-Key': 'AIzaSyDaJAHQw5wbURD3jboDHOzQaAgKxlxxZ_M',
            'X-API-Key' : os.getenv("SERPER_API_KEY"),
            #'X-API-Key': '926536e8a2896aec7800e6a258ac4077f02efda5'.
            'content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        #check if there is an organic key
        if "organic" not in response.json():
            return "Sorry, I couldn't find anything about that, there could be an error with your seprer api key."        
        else:
            results = response.json()["organic"]    
            string=[]
            print("Results",)
            return response.json()
    

