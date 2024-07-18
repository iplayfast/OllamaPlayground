import json
import aiohttp
import asyncio
import sys
import ollama
from typing import List, Dict, Any

async def get_value_of_parameter(param_name: str, parameters: List[Dict[str, Any]]) -> Any:
    matching_param = next((param for param in parameters if param['parameterName'] == param_name), None)
    if matching_param:
        return matching_param['parameterValue']
    return None  # or raise an exception, depending on your requirements

async def weather_from_lat_lon(latitude: str, longitude: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m&temperature_unit=fahrenheit&wind_speed_unit=mph&forecast_days=1"
        ) as response:
            json_data = await response.json()
            print(f"{json_data['current']['temperature_2m']} degrees Fahrenheit")

async def city_to_lat_lon(city: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://nominatim.openstreetmap.org/search?q={city}&format=json"
        ) as response:
            json_data = await response.json()
            return [json_data[0]['lat'], json_data[0]['lon']]

async def lat_lon_to_city(latitude: str, longitude: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"
        ) as response:
            json_data = await response.json()
            print(json_data['display_name'])

async def weather_from_location(location: str):
    lat_lon = await city_to_lat_lon(location)
    await weather_from_lat_lon(lat_lon[0], lat_lon[1])

async def web_search(query: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://localhost:3333/search?q={query}&format=json") as response:
            json_data = await response.json()
            print(f"{json_data['results'][0]['title']}\n{json_data['results'][0]['content']}\n")

city_to_lat_lon_tool = {
    "name": "CityToLatLon",
    "description": "get the latitude and longitude for a given city",
    "parameters": [
        {
            "name": "city",
            "description": "The city to get the latitude and longitude for",
            "type": "string",
            "required": True,
        },
    ],
}

weather_from_lat_lon_tool = {
    "name": "WeatherFromLatLon",
    "description": "Get the weather for a location",
    "parameters": [
        {
            "name": "latitude",
            "description": "The latitude of the location",
            "type": "number",
            "required": True,
        },
        {
            "name": "longitude",
            "description": "The longitude of the location",
            "type": "number",
            "required": True,
        },
    ],
}

lat_lon_to_city_tool = {
    "name": "LatLonToCity",
    "description": "Get the city name for a given latitude and longitude",
    "parameters": [
        {
            "name": "latitude",
            "description": "The latitude of the location",
            "type": "number",
            "required": True,
        },
        {
            "name": "longitude",
            "description": "The longitude of the location",
            "type": "number",
            "required": True,
        },
    ]
}

web_search_tool = {
    "name": "WebSearch",
    "description": "Search the web for a query",
    "parameters": [
        {
            "name": "query",
            "description": "The query to search for",
            "type": "string",
            "required": True,
        },
    ],
}

weather_from_location_tool = {
    "name": "WeatherFromLocation",
    "description": "Get the weather for a location",
    "parameters": [
        {
            "name": "location",
            "description": "The location to get the weather for",
            "type": "string",
            "required": True,
        },
    ],
}

tools_string = json.dumps(
    {
        "tools": [
            weather_from_location_tool,
            weather_from_lat_lon_tool,
            web_search_tool,
            lat_lon_to_city_tool,
            city_to_lat_lon_tool,
        ],
    },
    indent=2,
)

system_prompt = f"You are a helpful assistant that takes a question and finds the most appropriate tool or tools to execute, along with the parameters required to run the tool. Respond as JSON using the following schema: {{\"functionName\": \"functionName\", \"parameters\": [{{\"parameterName\": \"name of parameter\", \"parameterValue\": \"value of parameter\"}}]}}. The tools are: {tools_string}"

async def prompt_and_answer(prompt: str):
    # Note: Replace this with an appropriate Python library for language model interaction
    response = await generate_response(prompt)
    print(f"\nPrompt: {prompt}\n")
    print(f"Raw response: {response}\n")
    
    # Extract the JSON string from the 'response' field and parse it
    try:
        response_json = json.loads(response['response'].strip())
        print(f"Parsed response: {response_json}\n")
        
        result = await execute_function(response_json['functionName'], response_json['parameters'])
        print(f"Result: {result}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from response: {e}")
    except KeyError as e:
        print(f"Error accessing key in response: {e}")


async def generate_response(prompt: str):
    # Placeholder for language model interaction
    # Replace this with actual implementation using an appropriate Python library
    return ollama.generate(model='gemma2',prompt=prompt,system=system_prompt,format="json")
    return '{"functionName": "WeatherFromLocation", "parameters": [{"parameterName": "location", "parameterValue": "London"}]}'

async def execute_function(function_name: str, parameters: List[Dict[str, Any]]):
    print(function_name)
    if function_name == "WeatherFromLocation":
        return await weather_from_location(await get_value_of_parameter("location", parameters))
    elif function_name == "WeatherFromLatLon":
        return await weather_from_lat_lon(
            await get_value_of_parameter("latitude", parameters),
            await get_value_of_parameter("longitude", parameters),
        )
    elif function_name == "WebSearch":
        return await web_search(await get_value_of_parameter("query", parameters))
    elif function_name == "LatLonToCity":
        return await lat_lon_to_city(
            await get_value_of_parameter("latitude", parameters),
            await get_value_of_parameter("longitude", parameters),
        )
    elif function_name == "CityToLatLon":
        return await city_to_lat_lon(await get_value_of_parameter("city", parameters))

async def main():
    args = sys.argv[1:]
    if not args:
    #    print('Please provide a prompt')
    #    return
        prompt = ' What is the weather in london'
    else:
        prompt = ' '.join(args)
    try:
        await prompt_and_answer(prompt)
    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    asyncio.run(main())