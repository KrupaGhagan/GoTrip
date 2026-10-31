import httpx

from app.core.config import settings

from datetime import date, datetime, timedelta, timezone


async def get_weather(city: str) -> dict:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)

    response.raise_for_status()
    data = response.json()

    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "wind_speed_mps": data["wind"]["speed"],
    }



async def get_weather_forecast(
    city: str,
    start_date: date,
    number_of_days: int,
) -> dict:
    url = "https://api.openweathermap.org/data/2.5/forecast"

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            url,
            params={
                "q": city,
                "appid": settings.OPENWEATHER_API_KEY,
                "units": "metric",
            },
        )
        response.raise_for_status()
        data = response.json()

    # OpenWeather supplies the city's UTC offset in seconds.
    city_offset = timedelta(seconds=data["city"].get("timezone", 0))
    daily = {}

    for item in data.get("list", []):
        local_time = datetime.fromtimestamp(
            item["dt"], tz=timezone.utc
        ) + city_offset
        forecast_date = local_time.date()

        if not (start_date <= forecast_date < start_date + timedelta(days=number_of_days)):
            continue

        daily.setdefault(forecast_date.isoformat(), []).append(item)

    forecasts = []
    for forecast_date, items in sorted(daily.items()):
        temperatures = [item["main"]["temp"] for item in items]
        descriptions = [item["weather"][0]["description"] for item in items]

        forecasts.append({
            "date": forecast_date,
            "min_temp_c": round(min(temperatures), 1),
            "max_temp_c": round(max(temperatures), 1),
            "conditions": descriptions,
        })

    forecast_dates = {item["date"] for item in forecasts}
    requested_dates = [
        (start_date + timedelta(days=offset)).isoformat()
        for offset in range(number_of_days)
    ]

    return {
        "city": data["city"]["name"],
        "forecasts": forecasts,
        "unavailable_dates": [
            day for day in requested_dates if day not in forecast_dates
        ],
    }