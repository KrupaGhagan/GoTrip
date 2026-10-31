from fastapi import APIRouter, HTTPException, Query

from app.services.food_service import get_food_places

router = APIRouter()


@router.get("/")
async def get_food(
    city: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=20),
):
    try:
        places = await get_food_places(city, limit)

        return {
            "city": city,
            "count": len(places),
            "food_places": places,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not retrieve food places: {str(exc)}",
        )