import ollama from 'ollama';

function getValueOfParameter(paramName: string, parameters: { [name: string]: any }[]): any {
  const matchingParam = parameters.find((param) => param.parameterName === paramName);
  if (matchingParam) {
    return matchingParam.parameterValue;
  }
  return undefined; // or throw an error, depending on your requirements
}

async function WeatherFromLatLon(latitude: stirng, longitude:string) {
        const output = await fetch(
            `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m&temperature_unit=fahrenheit&wind_speed_unit=mph&forecase_days=1`,);
        const json = await output.json();
        console.log(`${json.current.temperature_2m}
            degrees Farenheit`);
}


async function CityToLatLon(city: string) {
        const output = await fetch(
            `https://nominatim.openstreetmap.org/search?q=${city}&format=json`,);
        const json = await output.json();
        return [json[0].lat, json[0].lon];
}
async function LatLonToCity(latitude: string, longitude: string) {
	const output = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`,)
	const json = await output.json();
	console.log(json.display_name);
}
async function WeatherFromLocation(location: string) {
	const latlon = await(CityToLatLon(location));
			     await WeatherFromLatLon(latlon[0],latlon[1]);
}
async function WebSearch(query: string) {
	const output = await fetch(`http://localhost:3333/search?q=${query}&format=json`,);
	const json = await output.json();
	console.log(`%{json.results[0].title}\n${json.results[0].content}\n`);
}

const cityToLatLonTool: Tool = {
	name: "CityToLatLon",
	description: "get the latitude and longitude for a given city",
	parameters: [
		{
			name: "city",
			description: "The city to get the latitude and longitude for",
			type: "string",
			required: true,
		},
	],
};

const weatherFromLatLonTool: Tool = {
	name: "WeatherFromLatLon",
	description: "Get the weather for a location",
	parameters: [
		{
			name: "latitude",
			description: "The latitude of the location",
			type: "number",
			required: true,
		},
		{
			name: "longitude",
			description: "The longitude of the location",
			type: "number",
			required: true,
		},
	],
};

const latlonToCityTool: Tool = {
	name: "LatLonToCity",
	description: "Get the city name for a given latitude and longitude",
	parameters: [
		{
			name: "latitude",
			description: "The latitude of the location",
			type: "number",
			required: true,
		},
		{
			name: "longitude",
			description: "The longitude of the location",
			type: "number",
			required: true,
		},
	]

};

const webSearchTool: Tool = {
	name: "WebSearch",
	description: "Search the web for a query",
	parameters: [
		{
			name: "query",
			description: "The query to search for",
			type: "string",
			required: true,
		},
	],
};

const weatherFromLocationTool: Tool = {
	name: "WeatherFromLocation",
	description: "Get the weather for a location",
	parameters: [
		{
			name: "location",
			description: "The location to get the weather for",
			type: "string",
			requried: true,
		},
	],
};


	
export const toolsString = JSON.stringify(
	{
		tools: [
			weatherFromLocationTool,
			weatherFromLatLonTool,
			webSearchTool,
			latlonToCityTool,
			cityToLatLonTool,

		],
	},
	null,
	2,
);

const systemPrompt = `You are a helpful assistant that takes a question and finds the most appropriate tool or tools to execute, along with the parameters requred to run the tool. Respond as JSON using the following schema: {"functionName": "functionName",
	"paramters": [{parameterName": "name of parameter", "parameterValue": "value of parameter"}]}, The tools are: ${toolsString}`;
const promptandanswer = async(prompt: string) => {
	const response = await ollama.generate({
		model: "mistral",
		system: systemPrompt,
		prompt: prompt,
		stream: false,
		format: "json",

	});
	console.log(`\n${prompt}\n`);
	const responseObject = JSON.parse(response.response.trim());
	console.log('\n${responseObject}\n');
	console.log(
	executeFunction(responseObject.functionName,responseObject.parameters)
	);

};

export async function executeFunction(
	functionName: string,
	parameters: FunctionParamater[],
){
	console.log(functionName);
	switch (functionName) {
		case "WeatherFromLocation":
			return await WeatherFromLocation(getValueOfParameter("location",parameters));

		case "WeatherfromLatLon":
			return await WeatherFromLatLon(
				getValueOfParameter("latitude",parameters),
				getValueOfParameter("longitude",parameters),
		);
		case "WebSearch":
			return await WebSearch(getValueOfParameter("query",parameters));
		case "LatLonToCity":
			return await LatLonToCity(
				getValueOfParameter("latitude",parameters),
				getValueOfParameter("longitude",parameters),
		);
		case "CityToLatLon":
			return await CityToLatLon(
				getValueOfParameter("latitude",parameters),
				getValueOfParameter("longitude",parameters),
		);
	}
}


//await promptandanswer("What is the weather in London?");

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error('Please provide a prompt');
    return;
  }
  const prompt = args.join(' ');
  try {
    await promptandanswer(prompt);
  } catch (error) {
    console.error(error);
  }
}


main();

