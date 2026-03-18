import requests
import pandas as pd
import time

# Curated list of top cities with some famous attractions
CITY_ATTRACTIONS = [
    {"city": "Tokyo", "lat": 35.6895, "lon": 139.6917},
    {"city": "Delhi", "lat": 28.7041, "lon": 77.1025},
    {"city": "Shanghai", "lat": 31.2304, "lon": 121.4737},
    {"city": "São Paulo", "lat": -23.5505, "lon": -46.6333},
    {"city": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"city": "Mexico City", "lat": 19.4326, "lon": -99.1332},
    {"city": "Beijing", "lat": 39.9042, "lon": 116.4074},
    {"city": "Osaka", "lat": 34.6937, "lon": 135.5023},
    {"city": "Cairo", "lat": 30.0444, "lon": 31.2357},
    {"city": "New York", "lat": 40.7128, "lon": -74.0060},
    {"city": "Dhaka", "lat": 23.8103, "lon": 90.4125},
    {"city": "Karachi", "lat": 24.8607, "lon": 67.0011},
    {"city": "Buenos Aires", "lat": -34.6037, "lon": -58.3816},
    {"city": "Kolkata", "lat": 22.5726, "lon": 88.3639},
    {"city": "Istanbul", "lat": 41.0082, "lon": 28.9784},
    {"city": "Chongqing", "lat": 29.4316, "lon": 106.9123},
    {"city": "Lagos", "lat": 6.5244, "lon": 3.3792},
    {"city": "Manila", "lat": 14.5995, "lon": 120.9842},
    {"city": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729},
    {"city": "Guangzhou", "lat": 23.1291, "lon": 113.2644},
    {"city": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
    {"city": "Moscow", "lat": 55.7558, "lon": 37.6173},
    {"city": "Kinshasa", "lat": -4.4419, "lon": 15.2663},
    {"city": "Tianjin", "lat": 39.3434, "lon": 117.3616},
    {"city": "Paris", "lat": 48.8566, "lon": 2.3522},
    {"city": "Shenzhen", "lat": 22.5429, "lon": 114.0596},
    {"city": "Jakarta", "lat": -6.2088, "lon": 106.8456},
    {"city": "London", "lat": 51.5074, "lon": -0.1278},
    {"city": "Bangalore", "lat": 12.9716, "lon": 77.5946},
    {"city": "Lima", "lat": -12.0464, "lon": -77.0428},
    {"city": "Chennai", "lat": 13.0827, "lon": 80.2707},
    {"city": "Seoul", "lat": 37.5665, "lon": 126.9780},
    {"city": "Bogotá", "lat": 4.7110, "lon": -74.0721},
    {"city": "Nagoya", "lat": 35.1815, "lon": 136.9066},
    {"city": "Ho Chi Minh City", "lat": 10.7769, "lon": 106.7009},
    {"city": "Bangkok", "lat": 13.7563, "lon": 100.5018},
    {"city": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    {"city": "Lahore", "lat": 31.5497, "lon": 74.3436},
    {"city": "Chicago", "lat": 41.8781, "lon": -87.6298},
    {"city": "Tehran", "lat": 35.6892, "lon": 51.3890},
    {"city": "Chengdu", "lat": 30.5728, "lon": 104.0668},
    {"city": "Nanjing", "lat": 32.0603, "lon": 118.7969},
    {"city": "Wuhan", "lat": 30.5928, "lon": 114.3055},
    {"city": "Ahmedabad", "lat": 23.0225, "lon": 72.5714},
    {"city": "Kuala Lumpur", "lat": 3.1390, "lon": 101.6869},
    {"city": "Xi'an", "lat": 34.3416, "lon": 108.9398},
    {"city": "Hong Kong", "lat": 22.3193, "lon": 114.1694},
    {"city": "Dongguan", "lat": 23.0207, "lon": 113.7518},
    {"city": "Hangzhou", "lat": 30.2741, "lon": 120.1551},
    {"city": "Foshan", "lat": 23.0215, "lon": 113.1214},
    {"city": "Shenyang", "lat": 41.8057, "lon": 123.4315},
    {"city": "Riyadh", "lat": 24.7136, "lon": 46.6753},
    {"city": "Baghdad", "lat": 33.3152, "lon": 44.3661},
    {"city": "Santiago", "lat": -33.4489, "lon": -70.6693},
    {"city": "Surat", "lat": 21.1702, "lon": 72.8311},
    {"city": "Madrid", "lat": 40.4168, "lon": -3.7038},
    {"city": "Suzhou", "lat": 31.2989, "lon": 120.5853},
    {"city": "Pune", "lat": 18.5204, "lon": 73.8567},
    {"city": "Harbin", "lat": 45.8038, "lon": 126.5349},
    {"city": "Houston", "lat": 29.7604, "lon": -95.3698},
    {"city": "Dallas", "lat": 32.7767, "lon": -96.7970},
    {"city": "Toronto", "lat": 43.6532, "lon": -79.3832},
    {"city": "Dar es Salaam", "lat": -6.7924, "lon": 39.2083},
    {"city": "Miami", "lat": 25.7617, "lon": -80.1918},
    {"city": "Belo Horizonte", "lat": -19.9167, "lon": -43.9345},
    {"city": "Singapore", "lat": 1.3521, "lon": 103.8198},
    {"city": "Philadelphia", "lat": 39.9526, "lon": -75.1652},
    {"city": "Atlanta", "lat": 33.7490, "lon": -84.3880},
    {"city": "Fukuoka", "lat": 33.5904, "lon": 130.4017},
    {"city": "Khartoum", "lat": 15.5007, "lon": 32.5599},
    {"city": "Barcelona", "lat": 41.3851, "lon": 2.1734},
    {"city": "Johannesburg", "lat": -26.2041, "lon": 28.0473},
    {"city": "Saint Petersburg", "lat": 59.9343, "lon": 30.3351},
    {"city": "Qingdao", "lat": 36.0671, "lon": 120.3826},
    {"city": "Dalian", "lat": 38.9140, "lon": 121.6147},
    {"city": "Washington D.C.", "lat": 38.9072, "lon": -77.0369},
    {"city": "Yangon", "lat": 16.8409, "lon": 96.1735},
    {"city": "Alexandria", "lat": 31.2001, "lon": 29.9187},
    {"city": "Jinan", "lat": 36.6512, "lon": 117.1201},
    {"city": "Guadalajara", "lat": 20.6597, "lon": -103.3496},
    {"city": "Chittagong", "lat": 22.3569, "lon": 91.7832},
    {"city": "Melbourne", "lat": -37.8136, "lon": 144.9631},
    {"city": "Shijiazhuang", "lat": 38.0428, "lon": 114.5149},
    {"city": "Abidjan", "lat": 5.3600, "lon": -4.0083},
    {"city": "Changsha", "lat": 28.2282, "lon": 112.9388},
    {"city": "Kunming", "lat": 24.8801, "lon": 102.8329},
    {"city": "Nairobi", "lat": -1.2921, "lon": 36.8219},
    {"city": "Shantou", "lat": 23.3710, "lon": 116.6819},
    {"city": "Hefei", "lat": 31.8206, "lon": 117.2272},
    {"city": "Rome", "lat": 41.9028, "lon": 12.4964},
    {"city": "Zhengzhou", "lat": 34.7466, "lon": 113.6254},
    {"city": "Changchun", "lat": 43.8171, "lon": 125.3236},
    {"city": "Kunshan", "lat": 31.3807, "lon": 120.9580},
    {"city": "Nanning", "lat": 22.8170, "lon": 108.3669},
    {"city": "Recife", "lat": -8.0476, "lon": -34.8770},
    {"city": "Baghdad", "lat": 33.3152, "lon": 44.3661},
    {"city": "Lisbon", "lat": 38.7169, "lon": -9.1390},
    {"city": "Kiev", "lat": 50.4501, "lon": 30.5234},
    {"city": "Belgrade", "lat": 44.8176, "lon": 20.4569},
]

def get_wikipedia_pageviews(title: str):
    """Get last 60 days of Wikipedia pageviews for a given title"""
    url = "https://en.wikipedia.org/w/api.php"
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

def get_coordinates(place_name, city_name):
    """Use OpenStreetMap Nominatim API to get coordinates of a place"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{place_name}, {city_name}",
        "format": "json",
        "limit": 1
    }
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "TopAttractionsScript"})
        data = res.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
    except:
        pass
    return None, None

# Collect data
rows = []
for city, attractions in CITY_ATTRACTIONS.items():
    for attraction in attractions:
        print(f"Processing {attraction} in {city}...")
        lat, lon = get_coordinates(attraction, city)
        popularity = get_wikipedia_pageviews(attraction)
        if lat and lon:
            rows.append({
                "city": city,
                "attraction": attraction,
                "lat": lat,
                "lon": lon,
                "popularity": popularity
            })
        time.sleep(1)  # polite delay to avoid overloading APIs

# Sort by popularity and keep top 100
df = pd.DataFrame(rows)
df = df.sort_values(by="popularity", ascending=False).head(100)

# Export CSV
df.to_csv("top_100_attractions.csv", index=False)
print("CSV file saved as top_100_attractions.csv")