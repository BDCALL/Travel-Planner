from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import random
import requests
from datetime import date, timedelta
import os

app = FastAPI(title="Smart Travel Planner Portfolio Version")

# -------------------- Data --------------------
CSV_FILE = "top100_cities_attractions.csv"

def load_data():
    return pd.read_csv(CSV_FILE)

class TravelRequest(BaseModel):
    city: str
    budget: int
    days: int
    preferences: Optional[List[str]] = None
    attractions_per_day: Optional[int] = 1  # default 1 if not specified
    start_date: Optional[date] = None       # optional start date

# -------------------- Geocoding --------------------
def geocode_city(city: str):
    """Get latitude and longitude from OpenStreetMap Nominatim API"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": city, "format": "json", "limit": 1}
        res = requests.get(url, params=params, headers={"User-Agent": "SmartTravelPlanner"})
        data = res.json()
        if data:
            return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
        return None
    except:
        return None

# -------------------- Attractions --------------------
def estimate_price(attraction):
    typ = attraction["type"].lower()
    base = {
        "museum": 10,
        "art": 12,
        "gallery": 8,
        "theme_park": 50,
        "monument": 5,
        "historic": 8,
        "viewpoint": 0,
        "park": 0
    }.get(typ, 10)
    if attraction.get("popularity", 0) > 100000:
        base *= 1.5
    return round(base)

def get_attractions(city: str, daily_budget: int):
    df = load_data()
    city_df = df[df["City"].str.lower() == city.lower()]
    attractions = []
    for _, row in city_df.iterrows():
        a = {
            "name": row["Attraction"],
            "type": row["Type"],
            "lat": row["Latitude"],
            "lon": row["Longitude"],
            "tag": row.get("Indoor", "Outdoor"),
            "popularity": row.get("Popularity", 0)
        }
        a["price"] = estimate_price(a)
        if a["price"] <= daily_budget:
            attractions.append(a)
    return attractions

# -------------------- Restaurants --------------------
def get_restaurants():
    return [
        {"name": "Casual Cafe", "type": "casual"},
        {"name": "Italian Bistro", "type": "italian"},
        {"name": "Sushi Spot", "type": "japanese"},
        {"name": "Steakhouse", "type": "steak"},
        {"name": "Fine Dining", "type": "fine dining"},
        {"name": "Street Food Hub", "type": "street food"},
        {"name": "Vegan Delight", "type": "vegan"},
        {"name": "Seafood Grill", "type": "seafood"},
        {"name": "BBQ House", "type": "bbq"},
        {"name": "Fusion Kitchen", "type": "fusion"}
    ]

def estimate_meal_cost(cuisine: str):
    cuisine = cuisine.lower()

    if "fine" in cuisine:
        return random.randint(60, 100)
    if "steak" in cuisine or "bbq" in cuisine:
        return random.randint(40, 70)
    if "seafood" in cuisine:
        return random.randint(35, 60)
    if "japanese" in cuisine:
        return random.randint(25, 45)
    if "italian" in cuisine or "fusion" in cuisine:
        return random.randint(20, 40)
    if "vegan" in cuisine:
        return random.randint(15, 30)
    if "street" in cuisine:
        return random.randint(8, 20)

    return random.randint(10, 25)

def get_price_category(price: int):
    if price < 20: return "$"
    if price < 40: return "$$"
    if price < 60: return "$$$"
    return "$$$$"

# -------------------- Real Weather --------------------
WEATHER_CODE_MAP = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Drizzle light", 53: "Drizzle moderate", 55: "Drizzle dense",
    56: "Freezing drizzle light", 57: "Freezing drizzle dense",
    61: "Rain slight", 63: "Rain moderate", 65: "Rain heavy",
    66: "Freezing rain light", 67: "Freezing rain heavy",
    71: "Snow fall slight", 73: "Snow fall moderate", 75: "Snow fall heavy",
    77: "Snow grains",
    80: "Rain showers slight", 81: "Rain showers moderate", 82: "Rain showers violent",
    85: "Snow showers slight", 86: "Snow showers heavy",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

def interpret_weather(precip, weather_code):
    if precip > 5:
        rain_desc = "Heavy rain"
    elif precip > 1:
        rain_desc = "Light rain"
    else:
        rain_desc = "No significant rain"
    code_desc = WEATHER_CODE_MAP.get(weather_code, "Unknown weather")
    return f"{code_desc}, {rain_desc}"

def get_real_weather(lat: float, lon: float, days: int, start_date: Optional[date] = None):
    start_date = start_date or (date.today() + timedelta(days=1))
    start_date_str = start_date.isoformat()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,weathercode",
        "forecast_days": days,
        "timezone": "auto",
        "start_date": start_date_str
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        daily = data.get("daily", {})
        weather_list = []
        for i in range(days):
            weather_list.append({
                "day": i + 1,
                "precipitation": daily.get("precipitation_sum", [0]*days)[i],
                "weathercode": daily.get("weathercode", [0]*days)[i]
            })
        return weather_list
    except:
        return [{"day": i+1, "precipitation": 0, "weathercode": 0} for i in range(days)]

# -------------------- API --------------------
@app.get("/cities")
def get_cities():
    try:
        df = load_data()
        cities = sorted(df["City"].unique())
        return JSONResponse(content=cities)
    except:
        return JSONResponse(content=[], status_code=500)

@app.get("/preferences")
def get_preferences(city: Optional[str] = None):
    try:
        df = load_data()
        if city:
            df = df[df["City"].str.lower() == city.lower()]
        types = sorted(df["Type"].dropna().unique())
        return JSONResponse(content=types)
    except:
        return JSONResponse(content=[], status_code=500)

@app.post("/plan")
def plan_trip(request: TravelRequest):
    city = request.city
    days = request.days
    prefs = request.preferences or []
    per_day = min(request.attractions_per_day or 1, 3)
    daily_budget = request.budget / days

    # Get coordinates dynamically
    coords = geocode_city(city)
    if not coords:
        return {"error": f"Could not get coordinates for {city}"}
    lat, lon = coords["lat"], coords["lon"]

    # Attractions
    all_attractions = get_attractions(city, daily_budget)
    if prefs:
        available_types = {a["type"] for a in all_attractions}
        prefs = [p for p in prefs if p in available_types]

    if not all_attractions:
        return {"error": "No attractions found within budget"}

    # Restaurants
    restaurants = get_restaurants()

    # Weather
    weather_forecast = get_real_weather(lat, lon, days, request.start_date)

    # Shuffle attractions to avoid same types in a day
    random.shuffle(all_attractions)
    available = all_attractions.copy()
    itinerary = []

    for day in range(days):
        raw_weather = weather_forecast[day]
        weather_str = interpret_weather(raw_weather["precipitation"], raw_weather["weathercode"])

        # Indoor/outdoor filtering
        if raw_weather["precipitation"] > 1:
            candidates = [a for a in available if a["tag"].lower() == "indoor"]
        else:
            candidates = [a for a in available if a["tag"].lower() == "outdoor"]

        if len(candidates) < per_day:
            candidates = available  # fallback

        # 🎯 SMART ATTRACTION SELECTION (uses budget better)
        candidates.sort(key=lambda a: a["price"], reverse=True)

        chosen = []
        used_types = set()

        for a in candidates:
            if len(chosen) >= per_day:
                break
            if a["type"] not in used_types:
                chosen.append(a)
                used_types.add(a["type"])

        # fill remaining if needed
        for a in candidates:
            if len(chosen) >= per_day:
                break
            if a not in chosen:
                chosen.append(a)

        for a in chosen:
            available.remove(a)
            
        # Restaurant
        attraction_cost = sum(a["price"] for a in chosen)
        remaining_budget = max(daily_budget - attraction_cost, 0)

        valid_restaurants = []
        for r in restaurants:
            price = estimate_meal_cost(r["type"])
            r_copy = r.copy()
            r_copy["price"] = price
            r_copy["category"] = get_price_category(price)
            valid_restaurants.append(r_copy)

        restaurant = min(
            valid_restaurants,
            key=lambda r: abs(r["price"] - remaining_budget)
        )


        itinerary.append({
            "day": day + 1,
            "attractions": [f"{a['name']} ({a['type']})" for a in chosen],
            "restaurant": f"{restaurant['name']} ({restaurant['type']}) - {restaurant['category']} ${restaurant['price']}",
            "weather": weather_str,
            "total_cost": attraction_cost + restaurant["price"]
        })

    start_date_str = request.start_date.isoformat() if request.start_date else (date.today() + timedelta(days=1)).isoformat()
    img_dir = "static/images_city"
    image_path = None
    for ext in ["jpeg","jpg","png"]:
        path = f"{img_dir}/{city.lower().replace(' ','_')}.{ext}"
        if os.path.isfile(path):
            image_path=f"/{path}"
            break
    return {
        "city": city,
        "total_budget": request.budget,
        "days": days,
        "preferences": prefs,
        "attractions_per_day": per_day,
        "start_date": start_date_str,
        "weather_forecast": [interpret_weather(w["precipitation"], w["weathercode"]) for w in weather_forecast],
        "itinerary": itinerary,
        "image" : image_path
    }

# -------------------- Serve Front-End --------------------
app.mount("/static", StaticFiles(directory="static", html=True), name="static")