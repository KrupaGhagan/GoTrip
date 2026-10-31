from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.services.planner_service import build_trip_plan

from app.services.gemini_service import generate_trip_summary

router = APIRouter()


@router.get("/")
async def create_trip_plan(
    destination: str = Query(..., min_length=2),
    start_date: date = Query(...),
    number_of_days: int = Query(..., gt=0, le=30),
    origin: str | None = Query(default=None, min_length=2),
    limit: int = Query(default=10, ge=1, le=20),
    mode: str = Query(default="drive"),
):
    try:
        return await build_trip_plan(
            destination=destination,
            start_date=start_date,
            number_of_days=number_of_days,
            origin=origin,
            limit=limit,
            mode=mode,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not build trip plan: {str(exc)}",
        )

@router.get("/ai-summary")
async def create_ai_trip_summary(
    destination: str = Query(..., min_length=2),
    start_date: date = Query(...),
    number_of_days: int = Query(..., gt=0, le=30),
    origin: str | None = Query(default=None, min_length=2),
    limit: int = Query(default=10, ge=1, le=20),
    mode: str = Query(default="drive"),
):
    # If building the trip plan fails, return an error as before.
    try:
        trip_data = await build_trip_plan(
            destination=destination,
            start_date=start_date,
            number_of_days=number_of_days,
            origin=origin,
            limit=limit,
            mode=mode,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not build trip plan: {str(exc)}",
        )

    # If Gemini fails, preserve trip_data and return a basic fallback.
    try:
        summary = await generate_trip_summary(trip_data)
        summary_source = "gemini"
    except Exception:
        summary = {
            "overview": (
                f"Your trip to {trip_data.get('destination', destination)} "
                "has been prepared. Review the trip data for details."
            ),
            "route_weather": (
                "An AI summary is temporarily unavailable. "
                "Review the route and weather data below."
            ),
            "places": [
                str(item.get("name", item))
                for item in (trip_data.get("places") or [])[:3]
            ],
            "stays": [
                str(item.get("name", item))
                for item in (trip_data.get("hotels") or [])[:3]
            ],
            "food_options": [
                str(item.get("name", item))
                for item in (trip_data.get("food_places") or [])[:3]
            ],
        }
        summary_source = "fallback"

    return {
        "trip_data": trip_data,
        "ai_summary": summary,
        "summary_source": summary_source,
    }