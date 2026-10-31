import httpx

from app.core.config import settings


def is_valid_food_place_name(name: str | None) -> bool:
    """Return True for named food places, excluding generic or missing names."""
    if not name:
        return False

    name_lower = name.strip().lower()
    if not name_lower:
        return False

    generic_names = {"catering", "restaurant", "cafe", "fast food"}
    return name_lower not in generic_names


async def get_food_places(city: str, limit: int = 10):
    if not settings.GEOAPIFY_API_KEY:
        raise RuntimeError("GEOAPIFY_API_KEY is not configured")

    async with httpx.AsyncClient(timeout=20) as client:
        # Convert the city name into coordinates.
        geocode_response = await client.get(
            "https://api.geoapify.com/v1/geocode/search",
            params={
                "text": city,
                "format": "json",
                "apiKey": settings.GEOAPIFY_API_KEY,
            },
        )
        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()

        if not geocode_data.get("results"):
            return []

        location = geocode_data["results"][0]
        lat = location["lat"]
        lon = location["lon"]

        # Find restaurants and cafés near the city center.
        places_response = await client.get(
            "https://api.geoapify.com/v2/places",
            params={
                "categories": "catering.restaurant,catering.cafe,catering.fast_food",
                "filter": f"circle:{lon},{lat},10000",
                "limit": limit,
                "apiKey": settings.GEOAPIFY_API_KEY,
            },
        )
        places_response.raise_for_status()
        places_data = places_response.json()

    food_places = []

    for feature in places_data.get("features", []):
        properties = feature.get("properties", {})
        name = properties.get("name")

        # Skip missing or generic names.
        if not is_valid_food_place_name(name):
            continue

        coordinates = feature.get("geometry", {}).get("coordinates", [])

        food_places.append({
            "name": name.strip(),
            "address": properties.get("formatted"),
            "categories": properties.get("categories", []),
            "longitude": coordinates[0] if len(coordinates) > 0 else None,
            "latitude": coordinates[1] if len(coordinates) > 1 else None,
            "place_id": properties.get("place_id"),
        })

    return food_places