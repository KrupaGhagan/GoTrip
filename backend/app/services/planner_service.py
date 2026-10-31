import asyncio

from app.services.weather_service import get_weather, get_weather_forecast
from app.services.places_service import search_places
from app.services.hotels_service import search_hotels
from app.services.food_service import get_food_places
from app.services.route_service import get_route_by_names
from datetime import date


async def build_trip_plan(
    destination: str,
    start_date: date,
    number_of_days: int,
    origin: str | None = None,
    limit: int = 10,
    mode: str = "drive",
) -> dict:
    weather, places, hotels, food = await asyncio.gather(
        get_weather_forecast(destination, start_date, number_of_days),
        search_places(destination, limit),
        search_hotels(destination, limit),
        get_food_places(destination, limit),
    )

    route = None
    if origin:
        route = await get_route_by_names(origin, destination, mode)

    return {
        "origin": origin,
        "destination": destination,
        "start_date": start_date,
        "number_of_days": number_of_days,
        "weather": weather,
        "places": places.get("places", []),
        "hotels": hotels.get("hotels", []),
        "food_places": food,
        "route": route,
    }