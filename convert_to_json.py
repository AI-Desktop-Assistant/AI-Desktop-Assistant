import json

# Step 1: Load and Prepare the Dataset
data = [
    {
        "sentence": "What is the weather in New York",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Show me the forecast for Los Angeles",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it raining in Chicago today",
        "labels": [
            "O",
            "O",
            "O",
            "PLACE",
            "O"
        ]
    },
    {
        "sentence": "Do I need an umbrella in Seattle",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the temperature in Miami",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "How hot is it in Phoenix",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is there snow in Denver",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather forecast for San Francisco",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Tell me the weather in Houston",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Will it rain tomorrow in Boston",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it sunny in San Diego",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "What will the weather be like in Las Vegas",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Check the weather for Washington DC",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the humidity level in Atlanta",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it cold in Minneapolis",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Do I need a jacket in Philadelphia",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "How is the weather in Orlando",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it snowing in Salt Lake City",
        "labels": [
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather like in Austin",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Show me the weather report for New Orleans",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather in Portland",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Tell me the forecast for Dallas",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "How windy is it in Nashville",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it raining in Charlotte",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the temperature in San Antonio",
        "labels": [
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Do I need an umbrella in Indianapolis",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it sunny in Kansas City",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather forecast for Columbus",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Show me the weather in Detroit",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Will it rain tomorrow in Memphis",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it cold in Milwaukee",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Do I need a jacket in Baltimore",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "How is the weather in Louisville",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it snowing in Albuquerque",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather like in Tucson",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Show me the weather report for Fresno",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather in Sacramento",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Tell me the forecast for Mesa",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "How windy is it in Omaha",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it raining in Virginia Beach",
        "labels": [
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather in Raleigh",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Tell me the forecast for Miami",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "How windy is it in Oklahoma City",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it raining in Cleveland",
        "labels": [
            "O",
            "O",
            "O",


            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the temperature in Tulsa",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Do I need an umbrella in Oakland",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it sunny in Long Beach",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather forecast for Arlington",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Show me the weather in Miami",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Will it rain tomorrow in Colorado Springs",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it cold in Wichita",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Do I need a jacket in New Orleans",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "How is the weather in Tampa",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it snowing in Anaheim",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather like in Honolulu",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Show me the weather report for Aurora",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather in St. Louis",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Tell me the forecast for Pittsburgh",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "How windy is it in Corpus Christi",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it raining in Lexington",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the temperature in Anchorage",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Do I need an umbrella in Stockton",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it sunny in Cincinnati",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather forecast for Henderson",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Show me the weather in Riverside",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Will it rain tomorrow in Newark",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it cold in Durham",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Do I need a jacket in Chandler",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "How is the weather in Madison",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it snowing in Lubbock",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather like in Gilbert",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Show me the weather report for Garland",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather in Plano",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Tell me the forecast for Lincoln",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "How windy is it in Buffalo",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it raining in Fort Wayne",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the temperature in Greensboro",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Do I need an umbrella in Jersey City",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it sunny in Chula Vista",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather forecast for St. Petersburg",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Show me the weather in Norfolk",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Will it rain tomorrow in Reno",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it cold in Winston-Salem",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Do I need a jacket in Irvine",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "How is the weather in Chesapeake",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it snowing in Scottsdale",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather like in North Las Vegas",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Show me the weather report for Fremont",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weatherin Baton Rouge",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "Tell me the forecast for Richmond",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "How windy is it in Boise",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it raining in San Bernardino",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the temperature in Spokane",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Do I need an umbrella in Montgomery",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it sunny in Des Moines",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather forecast for Modesto",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Show me the weather in Fayetteville",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Will it rain tomorrow in Shreveport",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it cold in Akron",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Do I need a jacket in Grand Rapids",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE",
            "PLACE"
        ]
    },
    {
        "sentence": "How is the weather in Huntsville",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Is it snowing in Mobile",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "What is the weather like in Augusta",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    },
    {
        "sentence": "Show me the weather report for Yonkers",
        "labels": [
            "O",
            "O",
            "O",
            "O",
            "O",
            "PLACE"
        ]
    }
]

with open('weather_dataset.json', 'w') as f:
    json.dump(data, f, indent=4)