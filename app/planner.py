# app/planner.py
def generate_itinerary(city: str, budget: int, days: int):
    daily_budget = budget // days
    itinerary = []
    for day in range(1, days + 1):
        itinerary.append({
            "day": day,
            "activity": f"Explore {city} attractions and try local cuisine",
            "estimated_cost": daily_budget
        })
    return itinerary