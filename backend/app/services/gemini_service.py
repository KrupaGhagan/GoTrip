import json
import os

from google import genai


def _prepare_summary_data(trip_data: dict) -> dict:
    """Prepare a compact, readable subset for Gemini without changing trip_data."""
    route = trip_data.get("route")

    if route:
        duration_seconds = route.get("duration_seconds")
        if duration_seconds is not None:
            total_minutes = round(duration_seconds / 60)
            hours, minutes = divmod(total_minutes, 60)
            route = {
                **route,
                "duration_readable": f"{hours} hours {minutes} minutes",
            }

    weather = trip_data.get("weather") or {}

    return {
        "origin": trip_data.get("origin"),
        "destination": trip_data.get("destination"),
        "start_date": trip_data.get("start_date"),
        "number_of_days": trip_data.get("number_of_days"),
        "route": route,
        "weather": weather,
        "places": (trip_data.get("places") or [])[:5],
        "hotels": (trip_data.get("hotels") or [])[:5],
        "food_places": (trip_data.get("food_places") or [])[:5],
    }

def validate_summary(summary: dict) -> dict:
    required_fields = {
        "overview": str,
        "route_weather": str,
        "places": list,
        "stays": list,
        "food_options": list,
    }

    if not isinstance(summary, dict):
        raise RuntimeError("Gemini summary must be a JSON object")

    for field, expected_type in required_fields.items():
        if field not in summary:
            raise RuntimeError(f"Gemini summary is missing field: {field}")

        if not isinstance(summary[field], expected_type):
            raise RuntimeError(
                f"Gemini summary field '{field}' has an invalid type"
            )

    for field in ("places", "stays", "food_options"):
        if not all(isinstance(item, str) for item in summary[field]):
            raise RuntimeError(
                f"Gemini summary field '{field}' must contain only strings"
            )

    return summary


async def generate_trip_summary(trip_data: dict) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=api_key)
    summary_data = _prepare_summary_data(trip_data)

    prompt = f"""
Create a concise trip overview using only the supplied data.

Return valid JSON with exactly these keys:
- overview: string
- route_weather: string
- places: array of strings
- stays: array of strings
- food_options: array of strings

Rules:
- Do not create a day-wise itinerary.
- Include at most 3 places, 3 stays, and 3 food options.
- Do not claim prices, availability, opening hours, or quality rankings.
- Treat listings as search results, not verified recommendations.
- Summarize weather accurately; mention rain or notable changes when present.
- Do not include markdown fences or text outside the JSON object.

Describe the listed weather conditions without implying their order or timing unless the forecast data explicitly provides it.

Trip data:
{json.dumps(summary_data, default=str, ensure_ascii=False)}
"""

    response = await client.aio.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")

    try:
        summary = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Gemini returned invalid JSON") from exc

    return validate_summary(summary)