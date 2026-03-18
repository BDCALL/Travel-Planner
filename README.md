# Smart Travel Planner

A web-based travel itinerary planner that generates personalized trip plans based on user preferences, budget, number of days, and starting date. Integrates real-time weather data and attractions information from OpenStreetMap.  

## Features

- Select city, budget, days, start date, and preferences
- Dynamic itinerary generation with indoor/outdoor logic based on weather
- Realistic restaurant suggestions with estimated price categories
- Supports multiple attractions per day (up to 3)
- Front-end interface served via FastAPI static files
- Automatic weather fetching using Open-Meteo API
- Avoids duplicate attractions and maximizes category diversity

## Tech Stack

- Python 3
- FastAPI
- Pandas
- Requests
- HTML/CSS/JS for front-end

## Setup

1. Clone the repository:

```bash
git clone https://github.com/BDCALL/Travel-Planner.git
cd Travel-Planner
```
2. Create a virutla environment and install depencies:
```bash
python3 -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
```
3. Run the app:
```bash
uvicorn app.main:app --reload
```
4. Open the front end in your browser:
```bash
http://127.0.0.1:8000/static/index.html
```

## Usage

- Choose a city from the dropdown (populated from CSV)
- Select number of days, budgets, attractions per day and perferences
- Click generate itinerary to get a personalized travel plan

## Notes

- Attractions and restaurants are filtered based on available data and user perferences
- Weather is fetched for the selected start days and upcoming days
- Maximum 3 attractions per day