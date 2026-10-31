import httpx
from fastapi import APIRouter, HTTPException, Query

from app.services.route_service import get_route_by_names

router = APIRouter()


@router.get("/")
async def calculate_route(
    origin: str = Query(min_length=1),
    destination: str = Query(min_length=1),
    mode: str = Query(default="drive", pattern="^(drive|walk|bicycle)$"),
):
    try:
        return await get_route_by_names(origin, destination, mode)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Geoapify returned HTTP {exc.response.status_code}",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Could not reach Geoapify",
        )