# app/main.py
from pydantic import BaseModel
from fastapi import FastAPI
from app.planner import generate_itinerary

app = FastAPI()

# Define what data we expect in the JSON body
class TravelRequest(BaseModel):
    city: str
    budget: int
    days: int


app = FastAPI(title="Smart Travel Planner API")

@app.get("/")
def root():
    return {"message": "Welcome to Smart Travel Planner!"}

@app.post("/plan")
def plan_trip(request: TravelRequest):
    # You can now access the JSON fields as Python attributes
    itinerary = [
        f"Day 1: Explore main attractions in {request.city}",
        f"Day 2: Try local food and markets",
        f"Day 3: Relax and enjoy the view"
    ]
    return {
        "city": request.city,
        "budget": request.budget,
        "days": request.days,
        "itinerary": itinerary
    }