import httpx

from app.core.config import settings

GEOCODE_URL = "https://api.geoapify.com/v1/geocode/search"
PLACES_URL = "https://api.geoapify.com/v2/places"


async def search_places(city: str, limit: int = 15) -> dict:
    if not settings.GEOAPIFY_API_KEY:
        raise RuntimeError("GEOAPIFY_API_KEY is not configured")

    async with httpx.AsyncClient(timeout=15) as client:
        # First, convert the city name into coordinates.
        geo_response = await client.get(
            GEOCODE_URL,
            params={
                "text": city,
                "format": "json",
                "limit": 1,
                "apiKey": settings.GEOAPIFY_API_KEY,
            },
        )
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        results = geo_data.get("results", [])
        if not results:
            return {"city": city, "places": []}

        location = results[0]
        lat = location["lat"]
        lon = location["lon"]

        # Then search for attractions around that location.
        places_response = await client.get(
            PLACES_URL,
            params={
                "categories": "tourism.attraction,tourism.sights",
                "filter": f"circle:{lon},{lat},10000",
                "limit": limit,
                "apiKey": settings.GEOAPIFY_API_KEY,
            },
        )
        places_response.raise_for_status()
        places_data = places_response.json()

    places = []
    for feature in places_data.get("features", []):
        properties = feature.get("properties", {})
        places.append({
            "name": properties.get("name"),
            "categories": properties.get("categories", []),
            "address": properties.get("address_line2")
                       or properties.get("address_line1"),
            "latitude": properties.get("lat"),
            "longitude": properties.get("lon"),
            "place_id": properties.get("place_id"),
        })

    return {
        "city": location.get("city") or city,
        "country": location.get("country"),
        "places": places,
    }