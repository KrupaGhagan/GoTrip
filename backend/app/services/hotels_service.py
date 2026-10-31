import httpx

from app.core.config import settings

GEOCODE_URL = "https://api.geoapify.com/v1/geocode/search"
PLACES_URL = "https://api.geoapify.com/v2/places"


def clean_hotel_name(name: str | None) -> bool:
    """Return True if the name looks like a valid hotel result."""
    if not name:
        return False

    name_lower = name.strip().lower()
    if not name_lower:
        return False

    food_terms = ("tiffin", "dhaba", "mess", "restaurant", "cafe")
    return not any(term in name_lower for term in food_terms)


async def search_hotels(city: str, limit: int = 15) -> dict:
    if not settings.GEOAPIFY_API_KEY:
        raise RuntimeError("GEOAPIFY_API_KEY is not configured")

    async with httpx.AsyncClient(timeout=15) as client:
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
        results = geo_response.json().get("results", [])

        if not results:
            return {"city": city, "hotels": []}

        location = results[0]
        lat, lon = location["lat"], location["lon"]

        hotel_response = await client.get(
            PLACES_URL,
            params={
                "categories": "accommodation.hotel",
                "filter": f"circle:{lon},{lat},10000",
                "limit": limit,
                "apiKey": settings.GEOAPIFY_API_KEY,
            },
        )
        hotel_response.raise_for_status()
        hotel_data = hotel_response.json()

    hotels = []
    for feature in hotel_data.get("features", []):
        properties = feature.get("properties", {})
        name = properties.get("name")

        # Skip missing names and results that appear to be food businesses.
        if not clean_hotel_name(name):
            continue

        hotels.append({
            "name": name.strip(),
            "address": (
                properties.get("address_line2")
                or properties.get("address_line1")
            ),
            "latitude": properties.get("lat"),
            "longitude": properties.get("lon"),
            "place_id": properties.get("place_id"),
        })

    return {
        "city": location.get("city") or city,
        "country": location.get("country"),
        "hotels": hotels,
    }