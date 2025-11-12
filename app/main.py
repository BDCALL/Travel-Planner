# app/main.py
from pydantic import BaseModel
from fastapi import FastAPI
from typing import List, Optional
from app.planner import generate_itinerary
import requests
import openrouteservice
from openrouteservice import convert


app = FastAPI(title="Smart Travel Planner API")

API_key = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjM2ZGQyZDM1NzVmNjRjOTRiN2Y2YjYxZmYyZTZiMzk0IiwiaCI6Im11cm11cjY0In0="

# Define what data we expect in the JSON body
class TravelRequest(BaseModel):
    city: str
    budget: int
    days: int
    preferences: Optional[List[str]] = None 

# Latitude and longitude for each city
CITY_COORDS = {
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Tokyo": {"lat": 35.6895, "lon": 139.6917},
    "London": {"lat": 51.5074, "lon": -0.1278}
}


def get_wikipedia_pageviews(title: str):
    """Get last 60 days of Wikipedia pageviews for a given title"""
    url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "pageviews",
        "titles": title,
        "format": "json"
    }
    try:
        res = requests.get(url, params=params)
        data = res.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            pageviews = page.get("pageviews", {})
            total_views = sum(v for v in pageviews.values() if isinstance(v, int))
            return total_views
    except:
        return 0

def get_attractions(city: str, lat: float, lon: float, preferences: Optional[List[str]] = None):
    url = "https://overpass-api.de/api/interpreter"
    
    query = f"""
    [out:json];
    (
      node["tourism"](around:10000,{lat},{lon});
      way["tourism"](around:10000,{lat},{lon});
      relation["tourism"](around:10000,{lat},{lon});
      node["historic"](around:10000,{lat},{lon});
      way["historic"](around:10000,{lat},{lon});
      relation["historic"](around:10000,{lat},{lon});
    );
    out center qt;
    """
    
    try:
        res = requests.get(url, params={"data": query}, timeout=60)
        data = res.json()
        elements = data.get("elements", [])
        print(f"Found {len(elements)} tourism/historic elements from Overpass API")  # Debug

        attractions = []
        for element in elements:
            tags = element.get("tags", {})
            name = tags.get("name")
            typ = tags.get("tourism") or tags.get("historic") or "unknown"
            if name:
                lat_el = element.get("lat") or element.get("center", {}).get("lat")
                lon_el = element.get("lon") or element.get("center", {}).get("lon")
                if lat_el and lon_el:
                    attractions.append({"name": name, "type": typ, "lat": lat_el, "lon": lon_el})

        # Filter by preferences if given
        if preferences:
            prefs_lower = [p.lower() for p in preferences]
            filtered = [
                a for a in attractions
                if any(pref in a["type"].lower() or pref in a["name"].lower() for pref in prefs_lower)
            ]
            if filtered:
                attractions = filtered

        return attractions[:15]  # top 15 attractions
    except Exception as e:
        print("Overpass API error:", e)
        return []

def get_weather(city: str, days: int):
    if city not in CITY_COORDS:
        return {"error": f"No coordinates found for {city}"}

    lat = CITY_COORDS[city]["lat"]
    lon = CITY_COORDS[city]["lon"]

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode"
        f"&forecast_days={days}&timezone=auto"
    )

    try:
        res = requests.get(url)
        data = res.json()

        # Collect simplified daily forecast
        daily_weather = []
        for i in range(days):
            daily_weather.append({
                "day": i + 1,
                "temp_max": data["daily"]["temperature_2m_max"][i],
                "temp_min": data["daily"]["temperature_2m_min"][i],
                "precipitation": data["daily"]["precipitation_sum"][i],
                "weathercode": data["daily"]["weathercode"][i]
            })
        return daily_weather
    except Exception as e:
        return {"error": str(e)}


def get_restaurants(city: str, lat: float, lon: float, preferences: Optional[List[str]] = None):
    """Get nearby restaurants from OpenStreetMap (Overpass API) and filter by user preferences."""
    url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node
      ["amenity"="restaurant"]
      (around:5000,{lat},{lon});
    out;
    """
    try:
        res = requests.get(url, params={"data": query})
        data = res.json()

        restaurants = []
        for element in data.get("elements", []):
            name = element.get("tags", {}).get("name", "Unnamed Restaurant")
            cuisine = element.get("tags", {}).get("cuisine", "unknown")
            restaurants.append({
                "name": name,
                "type": cuisine,
                "lat": element.get("lat"),
                "lon": element.get("lon")
            })

        # 🎯 Apply filtering by preferences
        if preferences:
            prefs_lower = [p.lower() for p in preferences]
            filtered = [
                r for r in restaurants
                if any(pref in r["type"].lower() or pref in r["name"].lower() for pref in prefs_lower)
            ]
            if filtered:
                restaurants = filtered

        return restaurants[:10]  # return top 10 for simplicity
    except Exception as e:
        print("Overpass error:", e)
        return []

@app.get("/")
def root():
    return {"message": "Welcome to Smart Travel Planner!"}

def get_travel_time(origin, destination):
    """Return driving distance and duration (in minutes)."""
    try:
        client = openrouteservice.Client(key=API_key)
        route = client.directions(
            coordinates=[origin, destination],
            profile='driving-car',
            format='geojson'
        )
        summary = route['features'][0]['properties']['summary']
        return {
            "distance_km": round(summary['distance'] / 1000, 2),
            "duration_min": round(summary['duration'] / 60, 1)
        }
    except Exception as e:
        return {"error": str(e)}
@app.post("/plan")
def plan_trip(request: TravelRequest):
    city = request.city
    days = request.days
    prefs = request.preferences or []

    # Get city coordinates
    coords = CITY_COORDS.get(city)
    if not coords:
        return {"error": f"Coordinates not found for {city}"}
    lat, lon = coords["lat"], coords["lon"]

    # Get attractions dynamically from Overpass API
    attractions = get_attractions(city, lat, lon, prefs)

    # Deduplicate attractions by name and coordinates
    unique_attractions = {}
    for a in attractions:
        key = (a["name"].lower(), round(a["lat"], 5), round(a["lon"], 5))
        if key not in unique_attractions:
            unique_attractions[key] = a
    attractions = list(unique_attractions.values())

    if not attractions:
        return {"error": f"No attractions found for {city}"}

    # Get restaurants dynamically from Overpass API
    restaurants = get_restaurants(city, lat, lon, prefs)

    # Weather forecast
    weather_forecast = get_weather(city, days)

    # Prepare itinerary
    itinerary = []
    available_attractions = attractions.copy()  # copy so we can remove used ones

    for day in range(1, days + 1):
        day_weather = weather_forecast[day - 1] if isinstance(weather_forecast, list) else {}
        precipitation = day_weather.get("precipitation", 0)

        # Choose indoor or outdoor attractions
        if precipitation > 2:  # rainy day
            candidates = [a for a in available_attractions if a["type"] in ["museum", "temple", "food"]]
        else:  # nice weather
            candidates = [a for a in available_attractions if a["type"] in ["landmark", "neighborhood", "sightseeing", "park"]]

        if not candidates:
            # fallback if no indoor/outdoor match left
            candidates = available_attractions

        if not candidates:
            break  # no attractions left

        chosen = candidates[0]  # pick the first available
        available_attractions.remove(chosen)  # remove to avoid repeats

        # Pick a restaurant (still cycles if days > number of restaurants)
        restaurant = restaurants[(day - 1) % len(restaurants)] if restaurants else {"name": "No restaurant", "type": ""}

        itinerary.append({
            "day": day,
            "attraction": f"{chosen['name']} ({chosen['type']})",
            "restaurant": f"{restaurant['name']} ({restaurant['type']})",
            "weather": day_weather
        })

    return {
        "city": city,
        "budget": request.budget,
        "days": days,
        "preferences": prefs,
        "weather forecast": weather_forecast,
        "itinerary": itinerary
    }