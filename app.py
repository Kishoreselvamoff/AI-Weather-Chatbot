# website/app.py
import os
from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()  # loads .env in project root if you run from website/ or parent

WEATHER_KEY = os.getenv("WEATHER_API_KEY")

app = Flask(__name__, template_folder="templates", static_folder="static")

if not WEATHER_KEY:
    print("WARNING: WEATHER_API_KEY not set in .env. Set WEATHER_API_KEY=your_key")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/weather")
def api_weather():
    """
    Query params:
    - city (string) OR lat & lon
    returns JSON with current weather and simplified 5-day forecast
    """
    city = request.args.get("city")
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not WEATHER_KEY:
        return jsonify({"error":"WEATHER_API_KEY not configured"}), 500

    if city:
        current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric"
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_KEY}&units=metric"
    elif lat and lon:
        current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_KEY}&units=metric"
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_KEY}&units=metric"
    else:
        return jsonify({"error":"Provide 'city' or 'lat' and 'lon'"}), 400

    # current weather
    cur_r = requests.get(current_url, timeout=10)
    if cur_r.status_code != 200:
        return jsonify({"error":"City not found or API error","details":cur_r.json()}), 404
    cur = cur_r.json()

    # 5-day forecast (3-hourly) -> reduce to 5 daily entries near 12:00
    f_r = requests.get(forecast_url, timeout=10)
    forecast = []
    if f_r.status_code == 200:
        fdata = f_r.json()
        # choose entries at 12:00 local time for next days
        chosen = {}
        for item in fdata.get("list", []):
            ts = item["dt"]
            dt = datetime.utcfromtimestamp(ts) + timedelta(seconds=fdata.get("city", {}).get("timezone", 0))
            key = dt.date()
            # prefer hour 12 (12:00)
            if key not in chosen:
                chosen[key] = item
            else:
                # replace if this item closer to 12:00
                prev_dt = datetime.utcfromtimestamp(chosen[key]["dt"]) + timedelta(seconds=fdata.get("city", {}).get("timezone", 0))
                if abs(dt.hour - 12) < abs(prev_dt.hour - 12):
                    chosen[key] = item
        # now sort and pick next 5 days (skip today)
        today = (datetime.utcnow() + timedelta(seconds=fdata.get("city", {}).get("timezone",0))).date()
        days = sorted([d for d in chosen.keys() if d > today])[:5]
        for d in days:
            item = chosen[d]
            dt = datetime.utcfromtimestamp(item["dt"]) + timedelta(seconds=fdata.get("city", {}).get("timezone", 0))
            forecast.append({
                "date": dt.strftime("%Y-%m-%d"),
                "temp": item["main"]["temp"],
                "desc": item["weather"][0]["description"],
                "icon": item["weather"][0]["icon"]
            })

    result = {
        "location": cur.get("name"),
        "country": cur.get("sys", {}).get("country"),
        "current": {
            "temp": cur["main"]["temp"],
            "feels_like": cur["main"].get("feels_like"),
            "desc": cur["weather"][0]["description"],
            "icon": cur["weather"][0]["icon"]
        },
        "forecast": forecast
    }
    return jsonify(result)

if __name__ == "__main__":
    # run from parent folder like: python website/app.py
    app.run(debug=True)
