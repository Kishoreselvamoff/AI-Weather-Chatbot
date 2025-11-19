# weather_only.py (rename to main.py if you want)

import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(city):
    if not WEATHER_KEY:
        return "Weather API key missing in .env!"

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric"
    response = requests.get(url).json()

    if response.get("cod") != 200:
        return "City not found."

    temp = response["main"]["temp"]
    desc = response["weather"][0]["description"]
    return f"Weather in {city}: {temp}°C, {desc}"

print("Weather Bot started! Type 'exit' to quit.")

while True:
    user = input("City name: ")

    if user.lower() == "exit":
        break

    print(get_weather(user))
