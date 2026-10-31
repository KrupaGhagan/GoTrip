import httpx
from fastapi import APIRouter, HTTPException, Query

from app.services.places_service import search_places

router = APIRouter()


@router.get("/")
async def get_places(
    city: str = Query(min_length=1),
    limit: int = Query(default=15, ge=1, le=50),
):
    try:
        return await search_places(city, limit)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Places provider returned HTTP {exc.response.status_code}",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Could not reach the places provider",
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))