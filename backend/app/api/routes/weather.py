from fastapi import APIRouter, HTTPException, Query
import httpx

from app.services.weather_service import get_weather

router = APIRouter()


@router.get("/")
async def weather(city: str = Query(min_length=1)):
    try:
        return await get_weather(city)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="City not found")
        if exc.response.status_code == 401:
            raise HTTPException(
                status_code=502,
                detail="Weather API key is invalid or not active",
            )
        raise HTTPException(status_code=502, detail="Weather provider error")
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Could not reach the weather provider",
        )