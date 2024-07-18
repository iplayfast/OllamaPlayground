import requests
import json
import ollama
import asyncio
from aiohttp import ClientSession

def get_value_of_parameter(param_name, parameters):
    matching_param = next((param for param in parameters if param['parameterName'] == param_name), None)
    return matching_param['parameterValue'] if matching_param else None

async def weather_from_lat_lon(latitude, longitude):
    url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m&temperature_unit=fahrenheit&wind_speed_unit=mph&forecast_days=1'
    async with ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    print(f'{data["current"]["temperature_2m"]} degrees Fahrenheit')

async def city_to_lat_lon(city):
    url = f'https://nominatim.openstreetmap.org/search?q={city}&format=json'
    async with ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    return data[0]['lat'], data[0]['lon']

async def lat_lon_to_city(latitude, longitude):
    url = f'https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json'
    async with ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    print(data['display_name'])

async def weather_from_location(location):
    lat, lon = await city_to_lat_lon(location)
    await weather_from_lat_lon(lat, lon)

async def web_search(query):
    url = f'http://localhost:3333/search?q={query}&format=json'
    async with ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    print(f'{data["results"][0]["title"]}\n{data["results"][0]["content"]}\n')

tools_data = {
    'tools': [
        {
            'name': 'WeatherFromLocation',
            'description': 'Get the weather for a location',
            'parameters': [{
                'name': 'location',
                'description': 'The location to get the weather for',
                'type': 'string',
                'required': True
            }]
        },
        {
            'name': 'WeatherFromLatLon',
            'description': 'Get the weather for a location',
            'parameters': [{
                'name': 'latitude',
                'description': 'The latitude of the location',
                'type': 'number',
                'required': True
            }, {
                'name': 'longitude',
                'description': 'The longitude of the location',
                'type': 'number',
                'required': True
            }]
        },
        {
            'name': 'WebSearch',
            'description': 'Search the web for a query',
            'parameters': [{
                'name': 'query',
                'description': 'The query to search for',
                'type': 'string',
                'required': True
            }]
        },
        {
            'name': 'LatLonToCity',
            'description': 'Get the city name for a given latitude and longitude',
            'parameters': [{
                'name': 'latitude',
                'description': 'The latitude of the location',
                'type': 'number',
                'required': True
            }, {
                'name': 'longitude',
                'description': 'The longitude of the location',
                'type': 'number',
                'required': True
            }]
        },
        {
            'name': 'CityToLatLon',
            'description': 'get the latitude and longitude for a given city',
            'parameters': [{
                'name': 'city',
                'description': 'The city to get the latitude and longitude for',
                'type': 'string',
                'required': True
            }]
        }
    ]
}
tools_string = json.dumps(tools_data, indent=2)

system_prompt = f"""You are a helpful assistant that takes a question and finds the most appropriate tool or tools to execute,
along with the parameters required to run the tool. Respond as JSON using the following schema: 
{{"functionName": "functionName",
        "parameters": [{{"parameterName": "name of parameter", "parameterValue": "value of parameter"}}]}}, 
The tools are: {tools_string}"""

async def prompt_and_answer(prompt):
    response = await ollama.generate(
        model="gemma2",
        system=system_prompt,
        prompt=prompt,
        stream=False,
        format="json"
    )
    return json.loads(response['response'])

async def execute_function(function_name, parameters):
    match function_name:
        case 'WeatherFromLocation':
            return await weather_from_location(get_value_of_parameter('location', parameters))
        case 'WeatherFromLatLon':
            return await weather_from_lat_lon(
                get_value_of_parameter('latitude', parameters),
                get_value_of_parameter('longitude', parameters)
            )
        case 'WebSearch':
            return await web_search(get_value_of_parameter('query', parameters))
        case 'LatLonToCity':
            return await lat_lon_to_city(
                get_value_of_parameter('latitude', parameters),
                get_value_of_parameter('longitude', parameters)
            )
        case 'CityToLatLon':
            return await city_to_lat_lon(get_value_of_parameter('city', parameters))

async def main():
    import sys
    if len(sys.argv) < 2:
        print('Please provide a prompt')
        return
    prompt = ' '.join(sys.argv[1:])
    try:
        response = await prompt_and_answer(prompt)
        await execute_function(response['functionName'], response['parameters'])
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(main())
