import httpx

from app.core.config import settings

ROUTING_URL = "https://api.geoapify.com/v1/routing"


async def get_route(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
    mode: str,
) -> dict:
    if not settings.GEOAPIFY_API_KEY:
        raise RuntimeError("GEOAPIFY_API_KEY is not configured")

    params = {
        "waypoints": (
            f"{origin_lat},{origin_lon}|"
            f"{destination_lat},{destination_lon}"
        ),
        "mode": mode,
        "format": "json",
        "apiKey": settings.GEOAPIFY_API_KEY,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(ROUTING_URL, params=params)
        response.raise_for_status()
        data = response.json()

    results = data.get("results", [])
    if not results:
        return {"route_found": False}

    route = results[0]

    return {
        "route_found": True,
        "mode": mode,
        "distance_meters": route.get("distance"),
        "duration_seconds": route.get("time"),
    }


import httpx

from app.core.config import settings

GEOCODE_URL = "https://api.geoapify.com/v1/geocode/search"


async def geocode_place(client: httpx.AsyncClient, place_name: str) -> tuple[float, float]:
    response = await client.get(
        GEOCODE_URL,
        params={
            "text": place_name,
            "format": "json",
            "limit": 1,
            "apiKey": settings.GEOAPIFY_API_KEY,
        },
    )
    response.raise_for_status()

    results = response.json().get("results", [])
    if not results:
        raise ValueError(f"Could not find location: {place_name}")

    return results[0]["lat"], results[0]["lon"]


async def get_route_by_names(origin: str, destination: str, mode: str) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        origin_lat, origin_lon = await geocode_place(client, origin)
        destination_lat, destination_lon = await geocode_place(client, destination)

        response = await client.get(
            "https://api.geoapify.com/v1/routing",
            params={
                "waypoints": (
                    f"{origin_lat},{origin_lon}|"
                    f"{destination_lat},{destination_lon}"
                ),
                "mode": mode,
                "format": "json",
                "apiKey": settings.GEOAPIFY_API_KEY,
            },
        )
        response.raise_for_status()
        data = response.json()

    routes = data.get("results", [])
    if not routes:
        return {"route_found": False}

    route = routes[0]
    distance_meters = route.get("distance")

    if distance_meters is None:
        distance_value = None
        distance_unit = None
    elif distance_meters >= 1000:
        distance_value = round(distance_meters / 1000, 2)
        distance_unit = "km"
    else:
        distance_value = round(distance_meters)
        distance_unit = "m"

    return {
        "route_found": True,
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "distance": distance_value,
        "distance_unit": distance_unit,
        "duration_seconds": route.get("time"),
    }